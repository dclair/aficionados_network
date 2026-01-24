from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse


# Esta función debe estar FUERA de la clase NotificationListView
@login_required
def notification_redirect(request, pk):
    # Buscamos la notificación asegurando que el destinatario sea el usuario actual
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)

    # Marcar como leída
    n.is_read = True
    n.save()

    # PRIORIDAD 1: Comentarios (Con salto al ancla #comment-id)
    if n.notification_type == "comment":
        if n.post and n.comment:
            url = reverse("posts:post_detail", kwargs={"pk": n.post.pk})
            return redirect(f"{url}#comment-{n.comment.id}")
        elif n.post:
            return redirect("posts:post_detail", pk=n.post.pk)

    # PRIORIDAD 2: Seguimiento
    elif n.notification_type == "follow":
        if n.sender and hasattr(n.sender, "profile"):
            return redirect("profiles:profile", pk=n.sender.profile.pk)

    # PRIORIDAD 3: Me gusta
    elif n.notification_type == "like" and n.post:
        return redirect("posts:post_detail", pk=n.post.pk)

    # --- NUEVA PRIORIDAD 4: Quedadas (Eventos) ---
    elif n.notification_type == "event" and n.event:
        # Redirigimos a la vista de detalle del evento que creamos
        return redirect("posts:event_detail", pk=n.event.pk)

    # Si no entra en ninguna categoría, vuelve a la lista de notificaciones
    return redirect("notifications:list")


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
