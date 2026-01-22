from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


# Esta función debe estar FUERA de la clase NotificationListView
@login_required
def notification_redirect(request, pk):
    # Buscamos la notificación (usando 'recipient' que es tu campo correcto)
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)

    # Marcar como leída
    n.is_read = True
    n.save()

    # --- LÓGICA DE REDIRECCIÓN POR TIPO (Ordenada correctamente) ---

    # 1. SI ES SEGUIMIENTO: Ir al perfil del que te ha seguido
    if n.notification_type == "follow":
        if n.sender and hasattr(n.sender, "profile"):
            return redirect("profiles:profile", pk=n.sender.profile.pk)

    # 2. SI ES COMENTARIO: Ir al post (y al ancla si fuera posible)
    elif n.notification_type == "comment":
        if n.post:
            # Aquí usamos el nombre de la ruta 'post_detail' y el ID del post
            # Si en el futuro añades el campo 'comment' al modelo, aquí pondremos el #ancla
            return redirect("posts:post_detail", pk=n.post.pk)

    # 3. SI ES LIKE: Ir al post
    elif n.notification_type == "like":
        if n.post:
            return redirect("posts:post_detail", pk=n.post.pk)

    # 4. CASO POR DEFECTO: Si algo falla, volver a la lista de notificaciones
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
