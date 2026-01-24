from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.utils import timezone

# Tus modelos y formularios
from .models import Posts, Event
from .forms import PostCreateForm, CommentForm, EventForm
from notifications.models import Notification


# --- VISTA PARA CREAR POST ---
# Añadimos LoginRequiredMixin para que no puedan crear si no están logueados
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Posts
    form_class = PostCreateForm
    template_name = "posts/post_create.html"
    success_url = reverse_lazy("home")
    login_url = "login"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# --- VISTA DE DETALLE DEL POST ---
# ¡CORRECCIÓN AQUÍ! LoginRequiredMixin debe ir ANTES que DetailView
class PostDetailView(LoginRequiredMixin, DetailView):
    model = Posts
    template_name = "posts/post_detail.html"
    context_object_name = "post"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        # Aprovechamos para pasar las aficiones si quisiéramos filtrar algo
        return context


# --- LÓGICA DE LIKES (Se mantiene igual, ya tiene el decorador) ---
@login_required
@require_POST
def toggle_like(request):
    p_id = request.POST.get("post_id")
    post = get_object_or_404(Posts, id=p_id)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
        if post.user != request.user:
            Notification.objects.get_or_create(
                recipient=post.user,
                sender=request.user,
                notification_type="like",
                post=post,
            )
    return JsonResponse({"liked": is_liked, "count": post.likes.count()})


# --- LÓGICA DE COMENTARIOS (Se mantiene igual) ---
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Posts, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()

            if post.user != request.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type="comment",
                    post=post,
                    comment=comment,
                )

            # Soporte para AJAX (si lo usas)
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                profile = getattr(request.user, "profile", None)
                avatar_url = (
                    profile.profile_picture.url
                    if profile and profile.profile_picture
                    else "/static/images/default-avatar.png"
                )

                return JsonResponse(
                    {
                        "success": True,
                        "comment": comment.comment,
                        "username": comment.user.username,
                        "avatar_url": avatar_url,
                        "comment_id": comment.id,
                        "created_at": "Ahora mismo",
                    }
                )

            return redirect("posts:post_detail", pk=post_id)
    return redirect("posts:post_detail", pk=post_id)


# Vista para CREAR la quedada
class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "posts/event_form.html"
    success_url = reverse_lazy("posts:event_list")
    login_url = "login"

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)


# Vista para VER la lista de quedadas
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "posts/event_list.html"
    context_object_name = "events"
    login_url = "login"

    def get_queryset(self):
        # Filtramos para ver solo eventos que no hayan pasado aún
        return Event.objects.filter(event_date__gte=timezone.now()).order_by(
            "event_date"
        )


# Función para APUNTARSE o DESAPUNTARSE
@login_required
def toggle_attendance(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user in event.participants.all():
        event.participants.remove(request.user)
    else:
        if event.participants.count() < event.max_participants:
            event.participants.add(request.user)

            # NUEVO: Notificar al organizador
            if event.organizer != request.user:
                Notification.objects.create(
                    recipient=event.organizer,
                    sender=request.user,
                    notification_type="comment",  # O añade "event" a tus tipos si prefieres
                    post=None,  # Los eventos no son posts, puede dejarse como None
                    # Podrías añadir un mensaje personalizado si tu modelo lo permite
                )
    return redirect("posts:event_detail", pk=event.id)


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "posts/event_detail.html"
    context_object_name = "event"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Esto nos servirá para mostrar quiénes están ya apuntados
        context["participants"] = self.object.participants.all()
        return context
