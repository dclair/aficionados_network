from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)
from django.views import View
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Posts, Event, Hobby
from .forms import PostCreateForm, CommentForm, EventForm, EventCommentForm
from notifications.models import Notification
from django.db.models import Q  # Importante para el buscador
from notifications.models import Notification as NotificationModel
from django.contrib import messages

# Busca esta línea (o similar) al principio de tu archivo:
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
)  # ... etc

# Y asegúrate de tener esta importación específica para la clase View:
from django.views import View  # <--- ¡ESTA ES LA QUE FALTA!


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
        # 1. Asignamos al usuario como organizador
        form.instance.organizer = self.request.user

        # 2. Guardamos el objeto primero para que tenga un ID en la base de datos
        response = super().form_valid(form)

        # 3. ¡Aquí está el truco! Añadimos al creador como participante
        self.object.participants.add(self.request.user)

        return response


# Vista para VER la lista de quedadas
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "posts/event_list.html"
    context_object_name = "events"
    login_url = "login"

    def get_queryset(self):
        # 1. OPTIMIZACIÓN: usamos select_related para traer los datos del Hobby
        # y del Organizador en una sola consulta (evita el error N+1)
        queryset = (
            Event.objects.select_related("hobby", "organizer")
            .filter(event_date__gte=timezone.now(), is_canceled=False)
            .order_by("event_date")
        )

        # 2. CAPTURA DE FILTROS
        search_query = self.request.GET.get("q")
        hobby_id = self.request.GET.get("hobby")

        # 3. FILTRADO DINÁMICO
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(location__icontains=search_query)
                | Q(
                    description__icontains=search_query
                )  # Añadido descripción para mejorar búsqueda
            )

        if hobby_id and hobby_id != "all":
            queryset = queryset.filter(hobby_id=hobby_id)

        # Usamos distinct() por si los filtros Q duplican resultados (aunque en este caso es raro)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Cargamos los hobbies para el select
        context["hobbies"] = Hobby.objects.all()
        # Valores para mantener el estado del formulario en la UI
        context["current_q"] = self.request.GET.get("q", "")
        context["current_hobby"] = self.request.GET.get("hobby", "all")
        return context


# Función para APUNTARSE o DESAPUNTARSE
@login_required
def toggle_attendance(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Si el que intenta cambiar su asistencia es el organizador, no le dejamos
    if request.user == event.organizer:
        messages.warning(
            request, "Como organizador, no puedes desapuntarte de tu propio evento."
        )
        return redirect("posts:event_detail", pk=event.id)

    if request.user in event.participants.all():
        event.participants.remove(request.user)
    else:
        if event.participants.count() < event.max_participants:
            event.participants.add(request.user)

            # --- Lógica de Notificación ---
            if event.organizer != request.user:
                NotificationModel.objects.create(
                    recipient=event.organizer,
                    sender=request.user,
                    notification_type="event",
                    event=event,  # Enlazamos la notificación a este evento
                )

    return redirect("posts:event_detail", pk=event.id)


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "posts/event_detail.html"
    context_object_name = "event"
    login_url = "login"

    def get_context_data(self, **kwargs):
        # 1. Obtenemos el diccionario base de Django (que ya trae al 'event')
        context = super().get_context_data(**kwargs)
        # 2. Obtenemos la lista de participantes
        context["participants"] = self.object.participants.all()
        # 3. Obtenemos la lista de comentarios
        context["comment_form"] = EventCommentForm()
        # 4. Devolvemos la caja de comentarios
        return context


# VISTA PARA EDITAR
class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    fields = [
        "title",
        "description",
        "location",
        "event_date",
        "max_participants",
        "hobby",
    ]
    template_name = "posts/event_form.html"  # Reutilizamos el mismo de crear

    def test_func(self):
        # Solo el organizador puede editar
        return self.get_object().organizer == self.request.user


# VISTA PARA (CANCELAR)
class EventCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        event = get_object_or_404(Event, pk=self.kwargs["pk"])
        return event.organizer == self.request.user

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        # 1. ESCUDO DE SEGURIDAD: Si ya está cancelado, salimos de aquí inmediatamente
        if event.is_canceled:
            messages.info(request, "Este evento ya ha sido cancelado anteriormente.")
            return redirect("posts:event_detail", pk=event.pk)

        # 2. MARCADO Y GUARDADO
        event.is_canceled = True
        event.save()

        # 3. NOTIFICAR SOLO UNA VEZ
        participants = event.participants.all()
        for p in participants:
            if p != request.user:
                Notification.objects.create(
                    recipient=p,
                    sender=request.user,
                    notification_type="event",
                    event=event,
                )

        messages.success(
            request,
            "El evento ha sido cancelado y los asistentes han sido notificados.",
        )
        return redirect("posts:event_detail", pk=event.pk)


# --- VISTA PARA COMENTAR EN UN EVENTO ---
@login_required
def add_event_comment(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        form = EventCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.event = event
            comment.user = request.user
            comment.save()

            # NOTIFICACIÓN al organizador
            if event.organizer != request.user:
                Notification.objects.create(
                    recipient=event.organizer,
                    sender=request.user,
                    notification_type="comment",
                    event=event,
                    content=f"ha comentado en tu evento: {event.title}",
                )

            messages.success(request, "Comentario publicado.")

    return redirect("posts:event_detail", pk=event.id)


# --- VISTA PARA VER MIS EVENTOS, los que él mismo ha creado ---
class MyEventsListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "posts/my_events.html"
    context_object_name = "my_events"
    paginate_by = 10  # Por si el usuario es muy activo

    def get_queryset(self):
        # Traemos todos sus eventos, ordenados del más reciente al más antiguo
        return Event.objects.filter(organizer=self.request.user).order_by("-event_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos la fecha actual para comparar en el HTML
        context["now"] = timezone.now()
        return context
