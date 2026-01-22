from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, FormView  # Añadida FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db import transaction  # Importante para ProfileUpdateView
from django.contrib import messages
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views import View
from aficionados_network.forms import UserUpdateForm, ProfileUpdateForm
from django.db.models import Exists, OuterRef
from notifications.models import Notification
from .models import UserProfile


from django.db.models import Exists, OuterRef  # Añade estas importaciones arriba


class ProfilesListView(ListView):
    model = UserProfile
    template_name = "profiles/profile_list.html"
    context_object_name = "profiles"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 1. Filtro de búsqueda (si existe)
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(user__username__istartswith=search_query)

        if user.is_authenticated:
            # 2. Excluirme a mí mismo de la lista
            queryset = queryset.exclude(user=user)

            # 3. ¡LA CLAVE! Anotamos si el usuario actual sigue a cada perfil de la lista
            # Comprobamos si el ID del perfil actual está en los seguidos del usuario logueado
            queryset = queryset.annotate(
                is_followed=Exists(user.profile.following.filter(pk=OuterRef("pk")))
            )

            # 4. Filtros de la barra lateral (Siguiendo / No siguiendo)
            filter_type = self.request.GET.get("filter", "all")
            if filter_type == "following":
                queryset = queryset.filter(is_followed=True)
            elif filter_type == "not_following":
                queryset = queryset.filter(is_followed=False)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            # 1. Total de perfiles (excluyéndome a mí)
            all_profiles_count = UserProfile.objects.exclude(user=user).count()

            # 2. Perfiles que ya sigo
            # Usamos la relación ManyToMany 'following' que tienes en tu modelo
            following_count = user.profile.following.count()

            # 3. Perfiles que NO sigo (Restamos: Total - Siguiendo)
            not_following_count = all_profiles_count - following_count

            # Pasamos los datos al contexto
            context["count_all"] = all_profiles_count
            context["count_following"] = following_count
            context["count_not_following"] = not_following_count
            context["active_filter"] = self.request.GET.get("filter", "all")

        return context


class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = "profiles/profile.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        pk_val = self.kwargs.get("pk")
        try:
            if not pk_val or (
                self.request.user.is_authenticated
                and str(self.request.user.profile.pk) == str(pk_val)
            ):
                return self.request.user.profile
            return super().get_object(queryset)
        except (UserProfile.DoesNotExist, AttributeError):
            raise Http404("El perfil no existe")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context["following_list"] = profile.following.all()
        context["followers_list"] = profile.followers.all()
        context["is_own_profile"] = self.get_object() == getattr(
            self.request.user, "profile", None
        )
        context["following_count"] = profile.following.count()
        context["followers_count"] = profile.followers.count()

        if self.request.user.is_authenticated:
            context["is_following"] = profile.followers.filter(
                pk=self.request.user.profile.pk
            ).exists()
        return context

    def post(self, request, *args, **kwargs):
        profile_id = request.POST.get("profile_pk")
        target_profile = get_object_or_404(UserProfile, pk=profile_id)
        current_user_profile = request.user.profile

        if current_user_profile.following.filter(pk=target_profile.pk).exists():
            # DEJAR DE SEGUIR
            current_user_profile.following.remove(target_profile)
            messages.success(
                request, f"Has dejado de seguir a {target_profile.user.username}"
            )
        else:
            # SEGUIR
            current_user_profile.following.add(target_profile)

            # --- INICIO LÓGICA DE NOTIFICACIÓN ---
            # Solo notificamos si no nos seguimos a nosotros mismos
            if target_profile.user != request.user:
                # Usamos get_or_create para no spamear si se siguen/desiguen muchas veces
                Notification.objects.get_or_create(
                    recipient=target_profile.user,  # El dueño del perfil seguido
                    sender=request.user,  # El usuario que pulsa el botón
                    notification_type="follow",
                    is_read=False,
                )
            # --- FIN LÓGICA DE NOTIFICACIÓN ---

            messages.success(request, f"Ahora sigues a {target_profile.user.username}")

        return redirect("profiles:profile", pk=target_profile.pk)


class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = "profiles/profile_edit.html"
    login_url = "login"

    def get(self, request, *args, **kwargs):
        profile = request.user.profile

        # DESCOMENTADO: Ahora sí creamos los formularios
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

        return render(
            request,
            self.template_name,
            {
                "user_profile": profile,
                "user_form": user_form,  # PASADO AL CONTEXTO
                "profile_form": profile_form,  # PASADO AL CONTEXTO
            },
        )

    def post(self, request, *args, **kwargs):
        profile = request.user.profile

        # Procesamos ambos formularios: datos de User y datos de Profile (incluida la foto)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "¡Perfil actualizado con éxito!")
            # Redirigimos al detalle del perfil para ver los cambios
            return redirect("profiles:profile", pk=profile.pk)

        # Si hay errores, volvemos a pintar el formulario con los errores
        return render(
            request,
            self.template_name,
            {
                "user_profile": profile,
                "user_form": user_form,
                "profile_form": profile_form,
            },
        )
