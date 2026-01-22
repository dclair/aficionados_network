from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


# Esta función debe estar FUERA de la clase NotificationListView
@login_required
def notification_redirect(request, pk):
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)
    n.is_read = True
    n.save()

    # PRIORIDAD 1: Comentarios (Con salto directo)
    if n.notification_type == "comment":
        if n.post and n.comment:
            # Te lleva al post y hace scroll automático al comentario
            return redirect(f"{n.post.get_absolute_url()}#comment-{n.comment.id}")
        elif n.post:
            return redirect(n.post.get_absolute_url())

    # PRIORIDAD 2: Seguimiento
    elif n.notification_type == "follow":
        return redirect("profiles:profile", pk=n.sender.profile.pk)

    # PRIORIDAD 3: Me gusta
    elif n.notification_type == "like" and n.post:
        return redirect(n.post.get_absolute_url())

    return redirect("notifications:notification_list")


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        # Solo queremos ver las notificaciones destinadas al usuario logueado
        return Notification.objects.filter(recipient=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Una vez que el usuario entra en la lista, las marcamos todas como leídas
        unread_notifications = self.get_queryset().filter(is_read=False)
        unread_notifications.update(is_read=True)
        return context
