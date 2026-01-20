from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = (
        "Notificaciones del Sistema"  # <-- Este es el nombre que saldrá en el Admin
    )

    def ready(self):
        import notifications.signals  # esto activa las señales
