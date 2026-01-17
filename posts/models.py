from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Posts(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name="Usuario"
    )
    # He añadido un título opcional por si decides usarlo
    title = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Título"
    )
    image = models.ImageField(
        upload_to="posts_images/", blank=True, null=True, verbose_name="Imagen"
    )
    caption = models.TextField(
        max_length=500, blank=True, null=True, verbose_name="Descripción"
    )
    # Añadido para que coincida con tu post_detail.html
    location = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Ubicación"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )
    likes = models.ManyToManyField(
        User, related_name="liked_posts", blank=True, verbose_name="Me gusta"
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.id} by {self.user.username} at {self.created_at}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Commentó {self.id} by {self.user.username} sobre el post {self.post} - {self.created_at}"
