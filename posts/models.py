# posts/models.py
from django.db import models
from django.contrib.auth.models import User
from profiles.models import Hobby
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image
import os
from django.urls import reverse


def validate_image_size(image):
    """Valida que la imagen no sea mayor a 5MB"""
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("La imagen no puede pesar más de 5MB")


class Posts(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name="usuario"
    )
    title = models.CharField(
        "título",
        max_length=200,
        blank=True,
        null=True,
        help_text="Título opcional para tu publicación",
    )
    image = models.ImageField(
        upload_to="posts_images/%Y/%m/%d/",
        blank=True,
        null=True,
        verbose_name="imagen",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
            validate_image_size,
        ],
        help_text="Formatos soportados: JPG, JPEG, PNG. Tamaño máximo: 5MB",
    )
    caption = models.TextField(
        "descripción",
        max_length=2000,
        blank=True,
        null=True,
        help_text="Comparte tus pensamientos (máx. 2000 caracteres)",
    )
    location = models.CharField(
        "ubicación",
        max_length=100,
        blank=True,
        null=True,
        help_text="¿Dónde se tomó esta foto?",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="fecha de actualización"
    )
    likes = models.ManyToManyField(
        User, related_name="liked_posts", blank=True, verbose_name="me gusta"
    )
    # este campo se usa para generar la url amigable
    slug = models.SlugField(
        max_length=255, unique=True, blank=True, null=True, verbose_name="slug"
    )
    # --- NUEVO CAMPO: Categoría por Afición ---
    category = models.ForeignKey(
        Hobby,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,  # Obligamos a elegir una para que tenga sentido la red
        related_name="posts",
    )

    class Meta:
        verbose_name = "publicación"
        verbose_name_plural = "publicaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        title = self.title or f"Publicación de {self.user.username}"
        return f"{title} - {self.created_at.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        # Primero guardamos el objeto para obtener un ID
        super().save(*args, **kwargs)

        # Verificar la relación following solo si el objeto ya tiene un ID
        if (
            hasattr(self, "_state")
            and not self._state.adding
            and hasattr(self, "following")
        ):
            # Verificar si el usuario se está siguiendo a sí mismo
            if self in self.following.all():
                from django.core.exceptions import ValidationError

                raise ValidationError("No puedes seguirte a ti mismo.")

        # Redimensionar imagen si existe
        if self.image:
            try:
                img = Image.open(self.image.path)
                if img.height > 1080 or img.width > 1080:
                    output_size = (1080, 1080)
                    img.thumbnail(output_size)
                    img.save(self.image.path, quality=85, optimize=True)
            except Exception as e:
                print(f"Error al procesar la imagen: {e}")

    def delete(self, *args, **kwargs):
        """Eliminar la imagen del sistema de archivos al eliminar el post"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    @property
    def total_likes(self):
        """Retorna el número total de 'me gusta'"""
        return self.likes.count()

    @property
    def total_comments(self):
        """Retorna el número total de comentarios"""
        return self.comments.count()

    def user_has_liked(self, user):
        """Verifica si un usuario ha dado like al post"""
        return self.likes.filter(pk=user.pk).exists()

    def get_absolute_url(self):
        # Asegúrate de que 'post_detail' es el nombre que usas en posts/urls.py
        return reverse("posts:post_detail", kwargs={"pk": self.pk})


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments", verbose_name="usuario"
    )
    post = models.ForeignKey(
        "Posts",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="publicación",
    )
    comment = models.TextField(
        "comentario",
        max_length=1000,
        help_text="Escribe tu comentario (máx. 1000 caracteres)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="fecha de actualización"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="comentario padre",
    )

    class Meta:
        verbose_name = "comentario"
        verbose_name_plural = "comentarios"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Comentario de {self.user.username} en {self.post}"

    @property
    def is_reply(self):
        """Verifica si el comentario es una respuesta a otro comentario"""
        return self.parent is not None

    @property
    def reply_count(self):
        """Retorna el número de respuestas a este comentario"""
        return self.replies.count()

    def clean(self):
        # Validar que el comentario no sea una respuesta a sí mismo
        if self.parent and self.parent == self:
            raise ValidationError("Un comentario no puede ser respuesta de sí mismo")

        # Validar que el comentario padre pertenezca al mismo post
        if self.parent and self.parent.post != self.post:
            raise ValidationError("El comentario padre debe pertenecer al mismo post")


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título de la quedada")
    description = models.TextField(verbose_name="Descripción del plan")
    location = models.CharField(max_length=255, verbose_name="Lugar de encuentro")
    event_date = models.DateTimeField(verbose_name="Fecha y hora del evento")
    image = models.ImageField(
        upload_to="events/", null=True, blank=True, verbose_name="Imagen de la quedada"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_canceled = models.BooleanField(default=False, verbose_name="¿Cancelado?")

    # RELACIONES
    # El usuario que crea la quedada
    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="events_created"
    )

    # A qué afición pertenece (Fotografía, Ciclismo, etc.)
    hobby = models.ForeignKey(Hobby, on_delete=models.CASCADE, related_name="events")

    # Lista de usuarios que se apuntan (Muchos a Muchos)
    participants = models.ManyToManyField(
        User, related_name="events_attending", blank=True
    )

    # Aforo máximo
    max_participants = models.PositiveIntegerField(
        default=10, verbose_name="Número máximo de asistentes"
    )

    @property
    def is_past(self):
        """Devuelve True si el evento ya ha pasado"""
        return self.event_date < timezone.now()

    def get_absolute_url(self):
        # Esto le dice a Django que la página "maestra" de un evento es su detalle
        return reverse("posts:event_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["event_date"]  # Los más próximos primero
        verbose_name = "Quedada"
        verbose_name_plural = "Quedadas"

    def __str__(self):
        return f"{self.title} - {self.hobby.name}"


class EventComment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]  # Los más antiguos primero (orden de conversación)

    def __str__(self):
        return f"Comentario de {self.user.username} en {self.event.title}"
