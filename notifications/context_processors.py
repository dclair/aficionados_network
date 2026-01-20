# notifications/context_processors.py
from .models import Notification


# esto lo que hace es que en cada template que se renderice, se le pasa el número de notificaciones no leídas
def unread_notifications(request):
    if request.user.is_authenticated:
        # Contamos las notificaciones no leídas para el usuario actual
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
    else:
        count = 0
    return {"unread_notifications_count": count}
