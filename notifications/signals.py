from django.db.models.signals import post_save
from django.dispatch import receiver

# Importa tu modelo de Seguidores (ajusta la ruta según tu app)
from profiles.models import Follow
from .models import Notification


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    # 'created' es True solo cuando se crea el registro por primera vez
    if created:
        Notification.objects.create(
            recipient=instance.followed_user,  # El que recibe el seguidor
            sender=instance.follower_user,  # El que dio clic en seguir
            notification_type="follow",
        )
