from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse


# Esta función debe estar FUERA de la clase NotificationListView
@login_required
def notification_redirect(request, pk):
    # Buscamos la notificación asegurando que el destinatario sea el usuario actual
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)

    # Marcar como leída
    n.is_read = True
    n.save()

    # --- CATEGORÍA: COMENTARIOS ---
    if n.notification_type == "comment":
        # CASO A: Es un comentario en un EVENTO (Quedada)
        if n.event:
            return redirect("posts:event_detail", pk=n.event.pk)

        # CASO B: Es un comentario en un POST (Publicación normal)
        if n.post:
            if n.comment:
                url = reverse("posts:post_detail", kwargs={"pk": n.post.pk})
                return redirect(f"{url}#comment-{n.comment.id}")
            return redirect("posts:post_detail", pk=n.post.pk)

    # --- CATEGORÍA: QUEDADAS (EVENTOS) ---
    elif n.notification_type == "event":
        if n.event:
            return redirect("posts:event_detail", pk=n.event.pk)

    # --- CATEGORÍA: SEGUIMIENTO ---
    elif n.notification_type == "follow":
        if n.sender and hasattr(n.sender, "profile"):
            # Ajustado a 'profiles:profile' según tu configuración
            return redirect("profiles:profile", pk=n.sender.profile.pk)

    # --- CATEGORÍA: ME GUSTA ---
    elif n.notification_type == "like" and n.post:
        return redirect("posts:post_detail", pk=n.post.pk)

    # Si por alguna razón el objeto (post/evento) fue borrado, volvemos a la lista
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


@login_required
def api_unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    # Si el contador es 0, podemos devolver un texto vacío o el número
    if count > 0:
        return HttpResponse(str(count))
    return HttpResponse("")
