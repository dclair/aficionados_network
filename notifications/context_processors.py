# notifications/context_processors.py
from .models import Notification


def unread_notifications(request):
    if request.user.is_authenticated:
        # Contamos las notificaciones no leídas para el usuario actual
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
    else:
        count = 0
    return {"unread_notifications_count": count}
