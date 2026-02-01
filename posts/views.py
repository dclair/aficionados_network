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
from django.db.models import Exists, OuterRef
from itertools import chain
from operator import attrgetter

# from notifications.models import Notification as NotificationModel
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views import View
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os
from .models import Event, Hobby
from profiles.models import Review
from django.db.models import Count  # Importante para contar los posts

# --- VISTA PARA CREAR POST ---
# Añadimos LoginRequiredMixin para que no puedan crear si no están logueados
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Posts
from django.shortcuts import render


# Funcion Maestra para enviar correos con el diseño de Hubs&Clicks
def send_hubs_email(subject, recipient, message_body, action_url):
    """
    Función universal para enviar correos con el diseño de Hubs&Clicks.
    """
    if not recipient.email:
        return  # Si no hay email, no hacemos nada

    context = {
        "recipient_name": recipient.username,
        "message_body": message_body,
        "action_url": action_url,
    }

    # 1. Renderizar el HTML y el texto plano
    html_content = render_to_string("general/emails/notification_email.html", context)
    text_content = strip_tags(html_content)

    # 2. Crear el objeto de email
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [recipient.email],
    )
    email.attach_alternative(html_content, "text/html")

    # 3. Adjuntar el Logo físicamente
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_hubs_email.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_data = f.read()
            logo_image = MIMEImage(logo_data)
            logo_image.add_header("Content-ID", "<logo_hubs_email>")
            email.attach(logo_image)

    # 4. Enviar
    email.send(fail_silently=True)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Posts
    form_class = PostCreateForm
    template_name = "posts/post_create.html"
    success_url = reverse_lazy("home")
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Posts para el Feed Global (Descubrimiento)
        context["global_posts"] = (
            Posts.objects.all()
            .select_related("user__profile", "category")
            .order_by("-created_at")[:12]
        )

        # 2. Estadísticas para el Cuadro de Bienvenida
        hoy = timezone.now().date()
        context["stats"] = {
            "posts_today": Posts.objects.filter(created_at__date=hoy).count(),
            "total_members": User.objects.count(),
            "new_this_week": Posts.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
        }
        # 3. Lógica de Tendencias
        # Contamos cuántos posts tiene cada categoría y traemos las 5 mejores
        from posts.models import (
            Hobby,
        )  # Asegúrate de importar tu modelo de Categoría/Afición

        context["trending_categories"] = (
            Hobby.objects.annotate(num_posts=Count("posts"))
            .filter(num_posts__gt=0)
            .order_by("-num_posts")[:5]
        )
        return context

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
def toggle_like(request, post_id):
    # 1. Buscamos el post
    post = get_object_or_404(Posts, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
        # 2. IMPORTANTE: Cambiamos recipient=post.author por recipient=post.user
        Notification.objects.filter(
            sender=user,
            recipient=post.user,  # <--- Corregido
            post=post,
            notification_type="like",
        ).delete()
    else:
        post.likes.add(user)
        liked = True

        # 3. Solo notificamos si el dueño del post no es quien da el like
        if post.user != user:  # <--- Corregido
            Notification.objects.create(
                sender=user,
                recipient=post.user,  # <--- Corregido
                post=post,
                notification_type="like",
            )

    # 4. Devolvemos la respuesta que el JS espera
    return JsonResponse({"liked": liked, "count": post.likes.count()})


# --- LÓGICA DE COMENTARIOS ---
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Posts, id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

            # 1. PREPARAR LA URL PARA EL BOTÓN DEL EMAIL
            action_url = request.build_absolute_uri(
                reverse("posts:post_detail", args=[post.pk])
            )

            # --- LÓGICA DE NOTIFICACIONES POR EMAIL ---

            # CASO A: Alguien externo comenta el post de otro usuario
            if post.user != request.user:
                # Notificación en la web (Campana)
                Notification.objects.create(
                    sender=request.user,
                    recipient=post.user,
                    notification_type="comment",
                    post=post,
                )

                # ENVÍO DE EMAIL (Usando la Función Maestra)
                send_hubs_email(
                    subject=f"💬 Nuevo comentario de @{request.user.username}",
                    recipient=post.user,
                    message_body=f'¡Hola! @{request.user.username} ha comentado en tu publicación: "{post.caption[:50]}..."',
                    action_url=action_url,
                )

            # CASO B: El dueño responde en su propio post
            else:
                # Buscamos quién más ha comentado aquí (excluyendo al dueño)
                participantes_ids = (
                    post.comments.exclude(user=post.user)
                    .values_list("user_id", flat=True)
                    .distinct()
                )
                usuarios_a_notificar = User.objects.filter(id__in=participantes_ids)

                for usuario in usuarios_a_notificar:
                    # Notificación en la web
                    Notification.objects.create(
                        sender=request.user,
                        recipient=usuario,
                        notification_type="comment",
                        post=post,
                    )

                    # ENVÍO DE EMAIL (Usando la Función Maestra)
                    send_hubs_email(
                        subject=f"📢 @{request.user.username} respondió en un post",
                        recipient=usuario,
                        message_body=f"El autor del post ha respondido en una conversación donde participaste.",
                        action_url=action_url,
                    )

    return redirect("posts:post_detail", pk=post.pk)


# --- VISTA PARA EDITAR POST ---
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Posts
    form_class = PostCreateForm
    template_name = "posts/post_update.html"

    def test_func(self):
        # Solo el autor puede editar
        post = self.get_object()
        return self.request.user == post.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtenemos posts de todos los usuarios para "Descubrir"
        # Usamos .order_by('?') para que sean aleatorios o '-created_at' para los últimos
        context["discover_posts"] = Posts.objects.exclude(pk=self.object.pk).order_by(
            "-created_at"
        )[:5]

        return context


# --- VISTA PARA ELIMINAR POST ---
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Posts
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("home")  # O 'posts:post_list'

    def test_func(self):
        # Solo el autor puede borrar
        post = self.get_object()
        return self.request.user == post.user


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
    paginate_by = 9

    def get_queryset(self):
        # 1. Con esto traemos los eventos futuros y no cancelados
        queryset = (
            Event.objects.select_related("hobby", "organizer")
            .filter(event_date__gte=timezone.now())
            .order_by("event_date")
        )

        # 2. Capturamos los filtros (incluyendo el nuevo de ciudad)
        search_query = self.request.GET.get("q")
        city_query = self.request.GET.get("city")  # <-- Nueva captura
        hobby_id = self.request.GET.get("hobby")

        # 3. Filtrado Dinámico
        # Texto general (Título, Ubicación o Descripción)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(location__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        # Filtro específico de Ciudad (si el usuario usa el campo dedicado)
        if city_query:
            queryset = queryset.filter(location__icontains=city_query)

        # Filtro por Hobby
        if hobby_id and hobby_id != "all":
            queryset = queryset.filter(hobby_id=hobby_id)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Cargamos los hobbies para el select
        context["hobbies"] = Hobby.objects.all()

        # Mantenemos TODOS los valores para que el formulario no se borre al pulsar "Filtrar"
        context["current_q"] = self.request.GET.get("q", "")
        context["current_city"] = self.request.GET.get("city", "")  # <-- Nuevo
        context["current_hobby"] = self.request.GET.get("hobby", "all")
        return context


# Función para APUNTARSE o DESAPUNTARSE
@login_required
def toggle_attendance(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user == event.organizer:
        messages.warning(request, "Como organizador, no puedes desapuntarte.")
        return redirect("posts:event_detail", pk=event.id)

    action_url = request.build_absolute_uri(
        reverse("posts:event_detail", args=[event.id])
    )

    if request.user in event.participants.all():
        event.participants.remove(request.user)
        messages.info(request, "Ya no estás apuntado.")
        # USAMOS LA FUNCIÓN MAESTRA
        send_hubs_email(
            f"🏃 Baja en tu evento: {event.title}",
            event.organizer,
            f"@{request.user.username} se ha desapuntado de tu evento '{event.title}'.",
            action_url,
        )
    else:
        if event.participants.count() < event.max_participants:
            event.participants.add(request.user)
            messages.success(request, "¡Te has apuntado!")
            # USAMOS LA FUNCIÓN MAESTRA
            send_hubs_email(
                f"✅ ¡Alguien se ha unido!: {event.title}",
                event.organizer,
                f"¡Buenas noticias! @{request.user.username} se ha unido a '{event.title}'.",
                action_url,
            )
        else:
            messages.error(request, "Evento lleno.")

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
        "image",
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

        if event.is_canceled:
            messages.info(request, "Este evento ya ha sido cancelado anteriormente.")
            return redirect("posts:event_detail", pk=event.pk)

        # 1. MARCADO DEL EVENTO
        event.is_canceled = True
        event.save()

        # 2. PREPARACIÓN DE DATOS PARA EL EMAIL
        action_url = request.build_absolute_uri(
            reverse("posts:event_detail", args=[event.pk])
        )
        subject = f"⚠️ Quedada cancelada: {event.title}"
        message_body = f"Lamentamos informarte que el plan '{event.title}' ha sido cancelado por el organizador. ¡No te preocupes! Pronto habrá más eventos disponibles."

        # 3. NOTIFICAR Y ENVIAR EMAILS A ASISTENTES
        participants = event.participants.all()
        for p in participants:
            if p != request.user:
                # Notificación visual (campanita roja)
                Notification.objects.create(
                    recipient=p,
                    sender=request.user,
                    notification_type="event",
                    event=event,
                )

                # --- ¡AQUÍ ESTÁ EL CAMBIO! ---
                # Usamos la función maestra que ya gestiona el LOGO y el HTML por dentro
                send_hubs_email(subject, p, message_body, action_url)

        messages.success(
            request,
            "El evento ha sido cancelado y los asistentes han sido notificados por email.",
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

            # URL para el botón del email
            action_url = request.build_absolute_uri(
                reverse("posts:event_detail", args=[event.id])
            )

            # --- LÓGICA DE NOTIFICACIONES ---

            if event.organizer != request.user:
                # CASO 1: Un usuario comenta -> El organizador recibe el aviso
                recipient = event.organizer

                # 1. Notificación web
                Notification.objects.create(
                    recipient=recipient,
                    sender=request.user,
                    notification_type="comment",
                    event=event,
                )

                # 2. EMAIL (USANDO LA FUNCIÓN MAESTRA)
                send_hubs_email(
                    f"💬 Nuevo comentario de {request.user.username}",
                    recipient,
                    f"{request.user.username} ha comentado en tu plan '{event.title}'.",
                    action_url,
                )

            else:
                # CASO 2: El organizador responde -> Todos los participantes reciben aviso
                participantes = event.participants.exclude(id=request.user.id)

                for pepe in participantes:
                    # 1. Notificación web para cada uno
                    Notification.objects.create(
                        recipient=pepe,
                        sender=request.user,
                        notification_type="comment",
                        event=event,
                    )

                    # 2. EMAIL (USANDO LA FUNCIÓN MAESTRA)
                    send_hubs_email(
                        f"📢 {request.user.username} ha respondido en: {event.title}",
                        pepe,
                        f"{request.user.username} (el organizador) ha puesto un comentario en el evento '{event.title}'.",
                        action_url,
                    )

            messages.success(request, "Comentario publicado y avisos enviados.")

    return redirect("posts:event_detail", pk=event.id)


# --- VISTA PARA VER MIS EVENTOS, los que uno mismo ha creado ---
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


# la siguiente clase es para reactivar un evento que se ha cancelado
class EventReactivateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        # Solo el organizador puede reactivar su propio evento
        event = get_object_or_404(Event, pk=self.kwargs["pk"])
        return self.request.user == event.organizer

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        ahora = timezone.now()

        # 1. VALIDACIÓN: ¿El evento ya pasó?
        if event.event_date <= ahora:
            messages.error(
                request, "No puedes reactivar un evento cuya fecha ya ha pasado."
            )
            return redirect("posts:event_detail", pk=event.pk)

        # 2. PROCESO DE REACTIVACIÓN
        if event.is_canceled:
            event.is_canceled = False
            event.save()

            # Preparar datos para las notificaciones
            action_url = request.build_absolute_uri(
                reverse("posts:event_detail", args=[event.id])
            )
            subject = f"✨ ¡Buenas noticias! Evento reactivado: {event.title}"
            message_body = f"¡El plan '{event.title}' ha sido reactivado por el organizador! Tu plaza sigue reservada. ¡Te esperamos!"

            # 3. NOTIFICAR A LOS PARTICIPANTES
            participants = event.participants.all()
            for p in participants:
                if p != request.user:
                    # A. Notificación en la web (campanita)
                    Notification.objects.create(
                        recipient=p,
                        sender=request.user,
                        notification_type="event",
                        event=event,
                    )

                    # B. Email Corporativo (Usando tu FUNCIÓN MAESTRA)
                    send_hubs_email(subject, p, message_body, action_url)

            messages.success(
                request, f"¡El evento '{event.title}' ha sido reactivado con éxito!"
            )
        else:
            messages.info(request, "El evento ya se encontraba activo.")

        return redirect("posts:event_detail", pk=event.id)


# la clase siguiente es para duplicar un evento
@login_required
def duplicate_event(request, pk):
    # 1. Buscamos el evento original (asegurándonos de que sea de el usuario que lo crea)
    original_event = get_object_or_404(Event, pk=pk, organizer=request.user)

    # 2. Creamos el nuevo evento copiando los campos
    new_event = Event.objects.create(
        title=f"COPIA: {original_event.title}",
        description=original_event.description,
        hobby=original_event.hobby,
        max_participants=original_event.max_participants,
        location=original_event.location,
        organizer=request.user,
        # Ponemos la misma fecha de momento, se cambiará en la edición
        event_date=original_event.event_date,
    )

    messages.success(
        request, f"Se ha duplicado el evento. ¡No olvides ajustar la fecha y el título!"
    )

    # 3. Redirigimos directamente al formulario de editar para los últimos ajustes
    return redirect("posts:event_update", pk=new_event.pk)


# clase para las vistas de los eventos en los que participo
class MyParticipationsListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "posts/my_participations.html"
    context_object_name = "participations"

    def get_queryset(self):
        # Buscamos eventos donde el usuario logueado está en la lista de participantes
        # 1. Obtenemos los eventos donde participa el usuario
        queryset = Event.objects.filter(participants=self.request.user).order_by(
            "-event_date"
        )
        # 2. Creamos una "subconsulta" para buscar reviews de Pepe en esos eventos
        user_reviews = Review.objects.filter(
            event=OuterRef("pk"),
            author=self.request.user,
        )

        # 3. "Anotamos" el queryset: añadimos el campo virtual 'has_reviewed' (True/False)
        return queryset.annotate(has_reviewed=Exists(user_reviews))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()  # Para saber si el evento ya pasó
        return context


# con esta funcion mostramos la galeria de clicks
def clicks_gallery(request):
    # 1. Extraemos Posts con imagen (no nula y no vacía)
    posts_with_img = Posts.objects.filter(image__isnull=False).exclude(image="")

    # 2. Extraemos Eventos con imagen (asumiendo que el campo se llama 'image')
    events_with_img = Event.objects.filter(image__isnull=False).exclude(image="")

    # 3. Los combinamos en una sola lista
    # Usamos chain para unirlos y sorted para ordenarlos por fecha de creación
    clicks = sorted(
        chain(posts_with_img, events_with_img),
        key=attrgetter("created_at"),  # Ordenamos por fecha
        reverse=True,  # Los más nuevos primero
    )

    return render(request, "posts/clicks_list.html", {"clicks": clicks})
