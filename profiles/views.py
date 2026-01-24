from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Exists, OuterRef
from django.contrib import messages
from django.http import Http404
from django.views import View

# Importaciones de tu proyecto
from aficionados_network.forms import UserUpdateForm, ProfileUpdateForm, AddHobbyForm
from notifications.models import Notification
from .models import UserProfile, UserHobby, Hobby


# --- LISTADO DE PERFILES ---
class ProfilesListView(ListView):
    model = UserProfile
    template_name = "profiles/profile_list.html"
    context_object_name = "profiles"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(user__username__istartswith=search_query)

        if user.is_authenticated:
            queryset = queryset.exclude(user=user)
            queryset = queryset.annotate(
                is_followed=Exists(user.profile.following.filter(pk=OuterRef("pk")))
            )
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
            all_profiles_count = UserProfile.objects.exclude(user=user).count()
            following_count = user.profile.following.count()
            context["count_all"] = all_profiles_count
            context["count_following"] = following_count
            context["count_not_following"] = all_profiles_count - following_count
            context["active_filter"] = self.request.GET.get("filter", "all")
        return context


# --- VISTA PÚBLICA DEL PERFIL (Solo lectura de aficiones) ---
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
        context["is_own_profile"] = profile == getattr(
            self.request.user, "profile", None
        )
        context["following_count"] = profile.following.count()
        context["followers_count"] = profile.followers.count()

        if self.request.user.is_authenticated:
            context["is_following"] = profile.followers.filter(
                pk=self.request.user.profile.pk
            ).exists()

        # Eliminado context["all_hobbies"] de aquí por seguridad y limpieza
        return context

    def post(self, request, *args, **kwargs):
        """Maneja el Follow/Unfollow"""
        profile_id = request.POST.get("profile_pk")
        target_profile = get_object_or_404(UserProfile, pk=profile_id)
        current_user_profile = request.user.profile

        if current_user_profile.following.filter(pk=target_profile.pk).exists():
            current_user_profile.following.remove(target_profile)
            messages.success(
                request, f"Has dejado de seguir a {target_profile.user.username}"
            )
        else:
            current_user_profile.following.add(target_profile)
            if target_profile.user != request.user:
                Notification.objects.get_or_create(
                    recipient=target_profile.user,
                    sender=request.user,
                    notification_type="follow",
                    is_read=False,
                )
            messages.success(request, f"Ahora sigues a {target_profile.user.username}")
        return redirect("profiles:profile", pk=target_profile.pk)


# --- VISTA DE EDICIÓN (Centro de gestión de Aficiones) ---
class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = "profiles/profile_edit.html"

    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

        # Pasamos los datos necesarios para gestionar hobbies en la misma página
        current_hobbies = UserHobby.objects.filter(profile=profile)
        all_hobbies = Hobby.objects.all()

        return render(
            request,
            self.template_name,
            {
                "user_profile": profile,
                "user_form": user_form,
                "profile_form": profile_form,
                "current_hobbies": current_hobbies,  # Listado para borrar
                "all_hobbies": all_hobbies,  # Listado para añadir
            },
        )

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "¡Perfil actualizado con éxito!")
            return redirect("profiles:profile", pk=profile.pk)

        return render(
            request,
            self.template_name,
            {
                "user_profile": profile,
                "user_form": user_form,
                "profile_form": profile_form,
            },
        )


# --- ACCIONES DE AFICIONES (Redirigen siempre a EDITAR) ---
@login_required
def add_hobby(request):
    if request.method == "POST":
        form = AddHobbyForm(request.POST)
        if form.is_valid():
            user_hobby = form.save(commit=False)
            user_hobby.profile = request.user.profile
            if not UserHobby.objects.filter(
                profile=user_hobby.profile, hobby=user_hobby.hobby
            ).exists():
                user_hobby.save()
                messages.success(request, "Afición añadida.")
            else:
                messages.warning(request, "Ya tienes esta afición en tu lista.")
    # Redirige a la edición, no al perfil público
    return redirect("profiles:profile_edit")


@login_required
def delete_hobby(request, hobby_id):
    user_hobby = get_object_or_404(UserHobby, id=hobby_id, profile=request.user.profile)
    user_hobby.delete()
    messages.success(request, "Afición eliminada.")
    # Redirige a la edición
    return redirect("profiles:profile_edit")
