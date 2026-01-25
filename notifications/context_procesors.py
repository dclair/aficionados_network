# notifications/context_processors.py
from .models import Notification


# con este context processor podemos acceder a la variable unread_count en cualquier template
def unread_notifications(request):
    if request.user.is_authenticated:
        # Contamos cuántas notificaciones tiene el usuario que NO estén leídas
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return {"unread_notifications_count": count}

    # Si no está logueado, el contador es 0
    return {"unread_notifications_count": 0}
