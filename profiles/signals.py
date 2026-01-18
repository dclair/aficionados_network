from django.db import transaction
from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a user profile when a new user is created.
    """
    if created and not instance.is_superuser:
        try:
            with transaction.atomic():
                UserProfile.objects.get_or_create(user=instance)
        except Exception as e:
            logger.error(
                f"Error creating profile for user {instance.username}: {str(e)}"
            )


@receiver(m2m_changed, sender=UserProfile.following.through)
def prevent_self_follow(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Prevent users from following themselves.
    """
    if action == "pre_add" and instance.pk in pk_set:
        from django.core.exceptions import ValidationError

        raise ValidationError("No puedes seguirte a ti mismo.")
