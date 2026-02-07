from django.contrib.admin import action
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DetailView,
    TemplateView,
    FormView,
    UpdateView,
    ListView,
)
from django.views.generic.edit import FormView
from .forms import ContactForm
from django.utils import timezone
from django.views import View
from django.contrib.auth import login, authenticate, logout, logout as auth_logout
from django.http import Http404, HttpResponseRedirect
from .forms import RegisterForm, LoginForm, UserUpdateForm, ProfileUpdateForm
from posts.forms import ProfileFollowForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from profiles.models import UserProfile, Follow, UserHobby
from django.contrib.auth.mixins import LoginRequiredMixin
from posts.models import Posts, Event
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


User = get_user_model()


class HomeView(TemplateView):
    template_name = "general/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- LÓGICA DE POSTS (Mantenida exactamente igual) ---
        last_posts = Posts.objects.none()
        if self.request.user.is_authenticated:
            has_profile = hasattr(self.request.user, "profile")
            context["has_profile"] = has_profile

            if not has_profile:
                last_posts = Posts.objects.all().order_by("-created_at")[:20]
            else:
                profile = self.request.user.profile
                seguidos = Follow.objects.filter(follower=profile).values_list(
                    "following__user", flat=True
                )
                last_posts = Posts.objects.filter(user__in=seguidos).order_by(
                    "-created_at"
                )[:20]
                if not last_posts.exists():
                    last_posts = Posts.objects.all().order_by("-created_at")[:20]
        else:
            last_posts = Posts.objects.all().order_by("-created_at")[:20]

        context["last_posts"] = last_posts

        # --- LÓGICA DE EVENTOS ---
        base_filter = Q(event_date__gte=timezone.now(), is_canceled=False)

        if self.request.user.is_authenticated and hasattr(self.request.user, "profile"):
            user_hobbies = self.request.user.profile.hobbies.all()

            if user_hobbies.exists():
                personal_filter = Q(hobby__in=user_hobbies) | Q(
                    organizer=self.request.user
                )

                events = (
                    Event.objects.filter(base_filter & personal_filter)
                    .select_related("hobby")
                    .distinct()
                    .order_by("event_date")[:5]
                )

                # --- NUEVA LÓGICA DE NIVELES PARA EL MATCH ---
                user_levels_qs = UserHobby.objects.filter(
                    profile=self.request.user.profile
                ).values("hobby_id", "level")

                levels_map = {
                    item["hobby_id"]: item["level"] for item in user_levels_qs
                }
                level_order = {
                    "beginner": 0,
                    "intermediate": 1,
                    "advanced": 2,
                    "expert": 3,
                }

                for event in events:
                    user_level = levels_map.get(event.hobby.id)
                    # Es match si es igual o el evento es para todos
                    event.is_match = (event.level == "all") or (
                        event.level == user_level
                    )

                    # Lógica de mentor (solo si no es "all")
                    if event.level != "all" and user_level:
                        event_val = level_order.get(event.level, -1)
                        user_val = level_order.get(user_level, 0)
                        event.is_mentor = user_val > event_val
                    else:
                        event.is_mentor = False

                context["upcoming_events"] = events
                context["filtered_by_hobbies"] = True
            else:
                context["upcoming_events"] = Event.objects.filter(base_filter).order_by(
                    "event_date"
                )[:5]
                context["filtered_by_hobbies"] = False
        else:
            context["upcoming_events"] = Event.objects.filter(base_filter).order_by(
                "event_date"
            )[:5]

        return context


class LoginView(FormView):
    template_name = "general/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"¡Bienvenido/a {username}!")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Usuario o contraseña incorrectos")
            return self.form_invalid(form)


class LogoutView(LoginRequiredMixin, View):
    """
    Vista segura para manejar el cierre de sesión solo mediante POST.
    """

    login_url = "login"

    def post(self, request, *args, **kwargs):
        auth_logout(request)
        messages.success(request, "Has cerrado sesión correctamente.")
        return redirect("home")

    # Si alguien intenta entrar por GET (escribiendo la URL),
    # lo redirigimos a inicio sin cerrar sesión, o a una página de confirmación.
    def get(self, request, *args, **kwargs):
        return redirect("home")


class RegisterView(CreateView):
    model = User
    template_name = "general/register.html"
    form_class = RegisterForm  # Tu formulario actual
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        # 1. Guardamos el usuario pero sin activar
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # 2. Generamos la lógica del email
        current_site = get_current_site(self.request)
        mail_subject = "Activa tu cuenta en Hubs & Clicks"

        context = {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        }

        # CAMBIO: Aquí lo llamamos html_content para que coincida con lo de abajo
        html_content = render_to_string("registration/acc_active_email.html", context)

        # 3. Enviamos el correo real
        to_email = form.cleaned_data.get("email")

        # Usamos EmailMultiAlternatives para el logo adjunto
        email = EmailMultiAlternatives(mail_subject, "", to=[user.email])
        email.attach_alternative(html_content, "text/html")

        # ADJUNTO: Logo hubs
        img_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_hubs.png")
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                logo = MIMEImage(f.read())
                logo.add_header("Content-ID", "<logo_id>")
                email.attach(logo)

        email.send()

        # 4. Mostramos la pantalla de "Revisa tu correo"
        return render(
            self.request, "registration/confirm_email_sent.html", {"email": to_email}
        )


# --- La función de activación ---
def activate(request, uidb64, token):
    try:
        # Decodificamos el ID del usuario de la URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Verificamos si el token es válido
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # --- CONFIGURACIÓN DEL EMAIL DE BIENVENIDA ---
        current_site = get_current_site(request)
        mail_subject = "¡Bienvenido a Hubs & Clicks!"

        # Renderizamos el HTML del correo
        html_content = render_to_string(
            "registration/welcome_email.html",
            {
                "user": user,
                "domain": current_site.domain,
            },
        )

        # Creamos el correo (EmailMultiAlternatives es necesario para adjuntos CID)
        email = EmailMultiAlternatives(mail_subject, "", to=[user.email])
        email.attach_alternative(html_content, "text/html")

        # Adjuntamos el logo como recurso relacionado (CID)
        img_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_hubs.png")

        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                logo = MIMEImage(f.read())
                # El ID <logo_id> debe coincidir con el src="cid:logo_id" del HTML
                logo.add_header("Content-ID", "<logo_id>")
                email.attach(logo)

        email.send()
        # -------------------------------------

        return render(request, "registration/activation_success.html")
    else:
        return render(request, "registration/activation_invalid.html")


class ProfilesListView(ListView):
    model = UserProfile
    template_name = "general/profile_list.html"
    context_object_name = "profiles"
    paginate_by = 12

    def get_queryset(self):
        from django.db.models import Q

        queryset = super().get_queryset()
        search_query = self.request.GET.get("q", "").strip()

        # Aplicar búsqueda si hay un término de búsqueda
        if search_query:
            # Buscar solo por nombre de usuario que empiece por el término de búsqueda
            queryset = queryset.filter(user__username__istartswith=search_query)

        if self.request.user.is_authenticated:
            # Excluir mi propio perfil
            queryset = queryset.exclude(user=self.request.user)

            filter_type = self.request.GET.get("filter", "all")

            if filter_type == "following":
                # Perfiles que sigo
                queryset = queryset.filter(
                    follower_relationships__follower=self.request.user.profile
                )

            elif filter_type == "not_following":
                # Perfiles que NO sigo
                queryset = queryset.exclude(
                    follower_relationships__follower=self.request.user.profile
                )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and hasattr(self.request.user, "profile"):
            current_profile = self.request.user.profile
            # Pasar el filtro activo a la plantilla
            context["active_filter"] = self.request.GET.get("filter", "all")

            # Obtener los IDs de los perfiles que sigue el usuario
            following_ids = set(
                Follow.objects.filter(follower=current_profile).values_list(
                    "following_id", flat=True
                )
            )

            # Asignar el estado de seguimiento a cada perfil
            for profile in context["profiles"]:
                profile.is_followed_by_user = profile.id in following_ids

        return context


class ProfileView(LoginRequiredMixin, DetailView, FormView):
    model = UserProfile
    template_name = "general/profile.html"
    context_object_name = "user_profile"
    form_class = ProfileFollowForm
    login_url = "/login/"  # URL a la que redirigir si no está autenticado
    redirect_field_name = "next"  # para volver a la página original después del login

    def get_object(self, queryset=None):
        """
        Obtiene el perfil solicitado o devuelve 404 si no existe.
        """
        try:
            # Si es el perfil del usuario actual
            if "pk" not in self.kwargs or str(self.request.user.profile.id) == str(
                self.kwargs.get("pk")
            ):
                # Si el usuario no tiene perfil, lanzamos DoesNotExist
                if not hasattr(self.request.user, "profile"):
                    raise UserProfile.DoesNotExist
                return self.request.user.profile
            # Si es otro perfil, comportamiento normal
            return super().get_object(queryset)
        except (UserProfile.DoesNotExist, AttributeError):
            if (
                self.request.user.is_authenticated
                and "pk" in self.kwargs
                and str(self.request.user.profile.id) == str(self.kwargs.get("pk"))
            ):
                # Redirigir a la creación de perfil si es el perfil del usuario actual
                messages.warning(
                    self.request, "Por favor, completa la información de tu perfil."
                )
                return None
            raise Http404("El perfil no existe")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()

        # Verificar si el usuario autenticado sigue a este perfil
        if self.request.user.is_authenticated and hasattr(self.request.user, "profile"):
            context["is_following"] = user_profile.followers.filter(
                id=self.request.user.profile.id
            ).exists()
        else:
            context["is_following"] = False

        return context

    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            action = form.cleaned_data["action"]
            profile_id = form.cleaned_data["profile_id"]
            target_profile = get_object_or_404(UserProfile, id=profile_id)

            if action == "follow":
                # Follow logic
                if not request.user.profile.following.filter(
                    id=target_profile.id
                ).exists():
                    request.user.profile.following.add(target_profile)
                    messages.success(
                        request, f"Ahora sigues a {target_profile.user.username}"
                    )
                else:
                    messages.info(
                        request, f"Ya sigues a {target_profile.user.username}"
                    )
            else:
                # Unfollow logic
                if request.user.profile.following.filter(id=target_profile.id).exists():
                    request.user.profile.following.remove(target_profile)
                    messages.success(
                        request,
                        f"Has dejado de seguir a {target_profile.user.username}",
                    )
                else:
                    messages.info(
                        request, f"No sigues a {target_profile.user.username}"
                    )

            return redirect("profile", pk=target_profile.id)
        else:
            messages.error(request, "Error en el formulario")
            return redirect("profile", pk=request.user.profile.id)


class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = "general/profile_edit.html"
    login_url = "login"

    def get_profile(self, user):
        """Obtiene o crea un perfil para el usuario de forma segura."""
        try:
            # Primero intentamos obtener el perfil existente
            return user.profile
        except UserProfile.DoesNotExist:
            # Si no existe, lo creamos sin acceder a relaciones many-to-many
            profile = UserProfile(user=user)
            profile.save()  # Guardamos para obtener un ID
            messages.info(
                self.request, "Por favor, completa la información de tu perfil."
            )
            return profile

    def get(self, request, *args, **kwargs):
        try:
            # Obtener o crear el perfil del usuario
            profile = self.get_profile(request.user)

            # Inicializar los formularios
            user_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileUpdateForm(instance=profile)

            return render(
                request,
                self.template_name,
                {
                    "user_form": user_form,
                    "profile_form": profile_form,
                    "user_profile": profile,
                },
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el perfil: {str(e)}")
            return redirect("home")

    def post(self, request, *args, **kwargs):
        try:
            # Obtener el perfil existente o crear uno nuevo
            profile = self.get_profile(request.user)

            # Inicializar los formularios con los datos del request
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(
                request.POST, request.FILES, instance=profile
            )

            if user_form.is_valid() and profile_form.is_valid():
                with transaction.atomic():
                    # 1. Guardar el usuario
                    user = user_form.save(commit=False)
                    user.save()

                    # 2. Guardar el perfil
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()

                    # 3. Manejar manualmente los campos many-to-many
                    for field_name, value in profile_form.cleaned_data.items():
                        if hasattr(profile, field_name) and hasattr(
                            getattr(profile, field_name), "set"
                        ):
                            getattr(profile, field_name).set(value)

                messages.success(request, "Perfil actualizado correctamente.")
                return redirect("profile_edit")
            else:
                # Mostrar errores de validación
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en {field}: {error}")
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en {field}: {error}")

                # Volver a mostrar el formulario con los errores
                return render(
                    request,
                    self.template_name,
                    {
                        "user_form": user_form,
                        "profile_form": profile_form,
                        "user_profile": profile,
                    },
                )

        except Exception as e:
            # Manejar cualquier error inesperado
            messages.error(
                request, f"Se produjo un error al guardar el perfil: {str(e)}"
            )
            # Redirigir a la misma página para volver a intentar
            return redirect("profile_edit")


class ContactFormView(FormView):
    template_name = "general/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        contact_message = form.save()

        # 1. Definimos los datos para la plantilla
        subject = f"📬 Nuevo mensaje: {contact_message.subject}"
        recipient_email = settings.CONTACT_EMAIL

        # El cuerpo del mensaje que irá dentro de {{ message_body }}
        full_message = (
            f"Has recibido un nuevo mensaje de contacto a través de la web.\n\n"
            f"👤 Nombre: {contact_message.name}\n"
            f"📧 Email: {contact_message.email}\n"
            f"📝 Mensaje:\n{contact_message.message}"
        )

        context = {
            "recipient_name": "Equipo de Hubs&Clicks",  # Quién recibe el mail (tú)
            "message_body": full_message,
            "action_url": self.request.build_absolute_uri("/admin/"),  # Link al panel
        }

        # 2. Renderizamos el HTML
        html_content = render_to_string("emails/notification_email.html", context)
        text_content = strip_tags(html_content)

        # 3. Creamos el objeto Email
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
        )
        email.attach_alternative(html_content, "text/html")

        # 4. Incrustamos el logo usando el ID exacto de tu plantilla: logo_hubs
        logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_hubs.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_image = MIMEImage(f.read())
                logo_image.add_header("Content-ID", "<logo_hubs>")
                email.attach(logo_image)

        # 5. Enviar
        email.send(fail_silently=False)

        messages.success(
            self.request, "Gracias por tu mensaje. Nos pondremos en contacto pronto."
        )
        return super().form_valid(form)
