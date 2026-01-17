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
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.http import Http404, HttpResponseRedirect
from .forms import RegisterForm, LoginForm, UserUpdateForm, ProfileUpdateForm
from posts.forms import ProfileFollowForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from profiles.models import UserProfile, Follow
from django.contrib.auth.mixins import LoginRequiredMixin
from posts.models import Posts
from django.contrib.auth.decorators import login_required


# FICHERO DE VIEWS PRINCIPAL/BASE
class HomeView(TemplateView):
    template_name = "general/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # si el usuario está logueado, haremos que aparezcan los posts de los usuarios que sigue
        # si no está logueado, mostramos los posts más recientes
        if self.request.user.is_authenticated:
            # Usuario autenticado: mostrar solo posts de usuarios que sigue
            seguidos = Follow.objects.filter(
                follower=self.request.user.profile
            ).values_list("following__user", flat=True)

            # Obtenemos los posts de los usuarios seguidos (sin incluir los propios)
            last_posts = Posts.objects.filter(user__in=seguidos).order_by(
                "-created_at"
            )[:15]
        else:
            # Usuario no autenticado
            last_posts = Posts.objects.all().order_by("-created_at")[:15]
        context["last_posts"] = last_posts
        return context


class LegalView(TemplateView):
    template_name = "general/legal.html"


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


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = "general/logout.html"
    login_url = "home"

    def get(self, request, *args, **kwargs):
        # Si el usuario no está autenticado, redirigir a home
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Verificar nuevamente la autenticación por seguridad
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, "Has cerrado sesión correctamente.")
        return redirect("home")


class RegisterView(CreateView):
    model = User
    template_name = "general/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        # Guarda el usuario en la base de datos
        response = super().form_valid(form)
        # Muestra el mensaje de éxito
        messages.success(
            self.request, "Usuario registrado correctamente. Inicia sesión."
        )
        # Redirige al login
        return redirect("login")


class ContactView(TemplateView):
    template_name = "general/contact.html"


class ProfilesListView(ListView):
    model = UserProfile
    template_name = "general/profile_list.html"
    context_object_name = "profiles"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()

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

        return queryset

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


class ProfileView(DetailView, FormView):
    model = UserProfile
    template_name = "general/profile_detail.html"
    context_object_name = "user_profile"
    form_class = ProfileFollowForm

    def form_valid(self, form):
        """
        Procesa el formulario cuando es válido.
        Se ejecuta cuando el usuario hace clic en el botón 'Seguir' o 'Dejar de seguir'.
        """
        # Obtener el ID del perfil del formulario
        profile_pk = form.cleaned_data.get("profile_pk")

        # Obtener el perfil que se va a seguir/dejar de seguir
        self.object = get_object_or_404(UserProfile, pk=profile_pk)

        # Obtener el perfil del usuario actual
        current_profile = self.request.user.profile

        # Verificar si el usuario actual ya sigue al perfil
        is_following = Follow.objects.filter(
            follower=current_profile, following=self.object
        ).exists()

        if is_following:
            # Si ya lo sigue, dejar de seguirlo
            Follow.objects.filter(
                follower=current_profile, following=self.object
            ).delete()
            messages.success(
                self.request,
                f"Dejaste de seguir a {self.object.user.username}",
                extra_tags="success",
            )
        else:
            # Si no lo sigue, seguirlo
            Follow.objects.create(follower=current_profile, following=self.object)
            messages.success(
                self.request,
                f"Ahora sigues a {self.object.user.username}",
                extra_tags="success",
            )

        # Limpiar mensajes existentes para evitar duplicados
        storage = messages.get_messages(self.request)
        storage.used = True

        return super().form_valid(form)

    def get_success_url(self):
        """
        Devuelve la URL a la que se redirigirá después de una acción exitosa.
        En este caso, redirige de vuelta al perfil que se acaba de seguir.
        """
        # Usamos reverse para construir la URL del perfil con el ID correspondiente
        return reverse("profile", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        """
        Especifica el conjunto de consultas que se utilizará para buscar el objeto.
        Usamos select_related para optimizar las consultas a la base de datos.
        """
        return UserProfile.objects.select_related("user")

    def get_context_data(self, **kwargs):
        """
        Añade datos adicionales al contexto que estará disponible en la plantilla.
        En este caso, añadimos si el usuario actual sigue al perfil que se está viendo.
        """
        # Obtener el contexto de la clase padre
        context = super().get_context_data(**kwargs)
        profile = self.object

        # Verificar si el usuario está autenticado
        if self.request.user.is_authenticated:
            # Añadir al contexto si el usuario actual sigue al perfil mostrado
            context["is_following"] = profile.is_followed_by(self.request.user.profile)
        else:
            # Si no está autenticado, por defecto no sigue a nadie
            context["is_following"] = False

        return context


class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = "general/profile_edit.html"

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "user_profile": request.user.profile,  # Añadido
            },
        )

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("profile_edit")

        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "user_profile": request.user.profile,  # Añadido
            },
        )
