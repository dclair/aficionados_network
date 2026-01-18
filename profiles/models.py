# profiles/models.py
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.storage import default_storage as storage
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date


def validate_birth_date(value):
    if value > date.today():
        raise ValidationError("La fecha de nacimiento no puede ser en el futuro")
    if value.year < 1900:
        raise ValidationError("Por favor ingrese una fecha de nacimiento válida")


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="usuario"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        default="profile_pictures/default_profile.png",
        verbose_name="foto de perfil",
        help_text="Sube una imagen cuadrada para mejor visualización",
    )
    bio = models.TextField(
        "biografía",
        blank=True,
        null=True,
        max_length=500,
        help_text="Cuéntanos sobre ti (máx. 500 caracteres)",
    )
    birth_date = models.DateField(
        "fecha de nacimiento", blank=True, null=True, validators=[validate_birth_date]
    )
    location = models.CharField(
        "ubicación", max_length=100, blank=True, null=True, help_text="Ciudad, País"
    )
    website = models.URLField(
        "sitio web", blank=True, null=True, help_text="Ej: https://tusitio.com"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="actualizado el")

    # Relación de seguidores
    followers = models.ManyToManyField(
        "self",
        through="Follow",
        through_fields=("following", "follower"),
        related_name="following",
        symmetrical=False,
        verbose_name="seguidores",
    )

    class Meta:
        verbose_name = "perfil de usuario"
        verbose_name_plural = "perfiles de usuario"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url
        return "/media/profile_pictures/default_profile.png"

    @property
    def followers_count(self):
        """Retorna el número de seguidores"""
        return self.follower_relationships.count()

    @property
    def following_count(self):
        """Retorna el número de usuarios que sigue"""
        return self.following_relationships.count()

    @property
    def age(self):
        """Retorna la edad del usuario si tiene fecha de nacimiento"""
        if not self.birth_date:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    def is_following(self, profile):
        """Verifica si este perfil está siguiendo a otro perfil"""
        return self.following_relationships.filter(following=profile).exists()

    def is_followed_by(self, profile):
        """Verifica si este perfil es seguido por otro perfil"""
        if not profile:
            return False
        return self.follower_relationships.filter(follower=profile).exists()

    def toggle_follow(self, profile):
        """Alterna el estado de seguimiento de un perfil"""
        if profile and profile != self:
            if self.is_following(profile):
                self.following_relationships.filter(following=profile).delete()
                return False
            Follow.objects.get_or_create(follower=self, following=profile)
            return True
        return None

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


class Follow(models.Model):
    """Relación de seguimiento entre perfiles."""

    follower = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="following_relationships",
        verbose_name="seguidor",
    )
    following = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="follower_relationships",
        verbose_name="siguiendo a",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="fecha de seguimiento"
    )

    class Meta:
        verbose_name = "seguimiento"
        verbose_name_plural = "seguimientos"
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Un usuario no puede seguirse a sí mismo")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower} sigue a {self.following}"
