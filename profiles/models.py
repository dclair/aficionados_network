from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.storage import default_storage as storage


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(
        "Imagen del perfil",
        upload_to="profile_pictures/",
        default="profile_pictures/default_profile.png",
    )
    bio = models.TextField("Biografía", blank=True, null=True)
    birth_date = models.DateField("Fecha de nacimiento", blank=True, null=True)
    location = models.CharField("Ubicación", max_length=100, blank=True, null=True)
    website = models.URLField("Website", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    # Relación de seguidores
    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        through="Follow",
        through_fields=("following", "follower"),
        related_name="following",
        blank=True,
        verbose_name="Seguidores",
    )

    @property
    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url
        return "/static/img/default_profile.png"

    # ==== AÑADE LOS NUEVOS MÉTODOS AQUÍ ====
    @property
    def followers_count(self):
        """Retorna el número de seguidores"""
        return self.follower_relationships.count()

    @property
    def following_count(self):
        """Retorna el número de usuarios que sigue"""
        return self.following_relationships.count()

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
            else:
                Follow.objects.get_or_create(follower=self, following=profile)
                return True
        return None

    # =======================================

    def save(self, *args, **kwargs):
        # Guardar primero para obtener la ruta de la imagen
        super().save(*args, **kwargs)

        # Redimensionar imagen si existe
        if self.profile_picture and hasattr(self.profile_picture, "path"):
            try:
                img = Image.open(self.profile_picture.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    # Guardar la imagen redimensionada
                    img.save(self.profile_picture.path, quality=90)
            except Exception as e:
                print(f"Error al procesar la imagen: {e}")

    def __str__(self):
        return f"Perfil de {self.user.username}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"


class Follow(models.Model):
    """Relación de seguimiento entre perfiles."""

    follower = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="following_relationships",
        verbose_name="Seguidor",
    )
    following = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="follower_relationships",
        verbose_name="Seguido",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Desde cuándo lo sigue"
    )

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.user.username} follows {self.following.user.username}"
