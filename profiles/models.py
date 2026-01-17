from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(
        "Imagen del perfil", upload_to="profile_pictures/", blank=True, null=True
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

    def followers_count(self):
        return self.follower_relationships.count()

    def following_count(self):
        return self.following_relationships.count()

    def is_following(self, profile):
        return self.following_relationships.filter(following=profile).exists()

    def is_followed_by(self, profile):
        if not profile:
            return False
        return self.follower_relationships.filter(follower=profile).exists()

    def follow(self, profile):
        if profile and profile != self:
            Follow.objects.get_or_create(follower=self, following=profile)

    def __str__(self):
        return self.user.username


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
