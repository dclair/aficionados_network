# modelo para mensajes de contacto

from django.db import models


class ContactMessage(models.Model):
    name = models.CharField("Nombre", max_length=100)
    email = models.EmailField("Correo electrónico")
    subject = models.CharField("Asunto", max_length=200)
    message = models.TextField("Mensaje")
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField("Leído", default=False)  # Para marcar si ya se revisó

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"
