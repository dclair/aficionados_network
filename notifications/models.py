from django.db import models

# from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    CHOICES = (
        ("follow", "Seguimiento"),
        ("like", "Me gusta"),
        ("comment", "Comentario"),
        ("event", "Quedada"),
        ("review", "Valoración"),
    )

    # Añadimos verbose_name a cada campo
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Destinatario",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        verbose_name="Remitente",
    )
    notification_type = models.CharField(
        max_length=20, choices=CHOICES, verbose_name="Tipo de notificación"
    )
    post = models.ForeignKey(
        "posts.Posts",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Publicación",
    )

    event = models.ForeignKey(
        "posts.Event",  # Apuntamos al modelo que creamos antes
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Quedada",
    )
    # valoraciones
    review = models.ForeignKey(
        "profiles.Review",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Valoración",
    )

    is_read = models.BooleanField(default=False, verbose_name="¿Leída?")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    # este campo es para cuando la notificación es de un comentario
    comment = models.ForeignKey(
        "posts.Comment", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        # Esto cambia el nombre de la sección en el Admin
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.get_notification_type_display()})"
