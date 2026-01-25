from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Exists, OuterRef, Avg
from django.contrib import messages
from django.http import Http404
from django.views import View
from django.utils import timezone

# Importaciones de tu proyecto
from aficionados_network.forms import UserUpdateForm, ProfileUpdateForm, AddHobbyForm
from notifications.models import Notification
from .models import UserProfile, UserHobby, Hobby, Review
from posts.models import Event
from .forms import ReviewForm
from notifications.models import Notification


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


# --- VISTA PÚBLICA DEL PERFIL (Vitaminada con Eventos) ---
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

        # --- NUEVAS ESTADÍSTICAS (VITAMINAS) ---
        # 1. Eventos que ha organizado (Juan style)
        context["organized_count"] = Event.objects.filter(
            organizer=profile.user
        ).count()

        # 2. Eventos a los que se ha apuntado (Pepe style)
        context["participated_count"] = Event.objects.filter(
            participants=profile.user
        ).count()

        # 3. Próxima actividad (Agenda)
        context["upcoming_activity"] = Event.objects.filter(
            participants=profile.user, event_date__gte=timezone.now(), is_canceled=False
        ).order_by("event_date")[:3]

        # --- Lógica de seguidores existente ---
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

        # NUEVO: Calculamos la media de valoraciones recibidas
        average_rating = Review.objects.filter(recipient=profile.user).aggregate(
            Avg("rating")
        )["rating__avg"]
        context["average_rating"] = round(average_rating, 1) if average_rating else 0
        context["total_reviews"] = Review.objects.filter(recipient=profile.user).count()

        # 1. Traemos las reseñas recibidas, ordenadas por la más reciente
        context["received_reviews"] = (
            Review.objects.filter(recipient=profile.user)
            .select_related("author")
            .order_by("-created_at")
        )

        # 2. El cálculo de la media que ya teníamos
        average_rating = context["received_reviews"].aggregate(Avg("rating"))[
            "rating__avg"
        ]
        context["average_rating"] = round(average_rating, 1) if average_rating else 0
        context["total_reviews"] = context["received_reviews"].count()

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


# --- VISTA DE EDICIÓN ---
class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = "profiles/profile_edit.html"

    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

        current_hobbies = UserHobby.objects.filter(profile=profile)
        all_hobbies = Hobby.objects.all()

        return render(
            request,
            self.template_name,
            {
                "user_profile": profile,
                "user_form": user_form,
                "profile_form": profile_form,
                "current_hobbies": current_hobbies,
                "all_hobbies": all_hobbies,
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


# --- ACCIONES DE AFICIONES ---
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
    return redirect("profiles:profile_edit")


# para eliminar una afición
@login_required
def delete_hobby(request, hobby_id):
    user_hobby = get_object_or_404(UserHobby, id=hobby_id, profile=request.user.profile)
    user_hobby.delete()
    messages.success(request, "Afición eliminada.")
    return redirect("profiles:profile_edit")


# para valorar un evento
@login_required
def add_review(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # 1. SEGURIDAD: Evitar que se valore dos veces el mismo evento
    if Review.objects.filter(author=request.user, event=event).exists():
        messages.warning(request, "Ya has enviado una valoración para este evento.")
        return redirect("posts:my_participations")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            # 2. GUARDAR LA VALORACIÓN
            review = form.save(commit=False)
            review.event = event
            review.author = request.user
            review.recipient = event.organizer
            review.save()

            # 3. LANZAR NOTIFICACIÓN (Usando tu modelo de la app notifications)
            Notification.objects.create(
                recipient=event.organizer,  # Juan recibe
                sender=request.user,  # Pepe envía
                notification_type="review",
                event=event,  # Enlazamos la quedada
                review=review,  # Enlazamos la reseña
            )

            messages.success(request, "¡Valoración enviada y notificada con éxito!")
        else:
            error_msg = f"Error en el formulario: {form.errors.as_text()}"
            messages.error(request, error_msg)
            print(error_msg)

    return redirect("posts:my_participations")


# leer y redirigir a la lista de notificaciones
@login_required
def read_and_redirect(request, notification_id):
    # 1. Buscamos la notificación
    n = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    # 2. La marcamos como leída
    n.is_read = True
    n.save()

    # 3. ¿A dónde lo mandamos? (Lógica de redirección)
    if n.notification_type == "review":
        return redirect("profiles:profile", pk=n.recipient.profile.pk)

    if n.notification_type in ["like", "comment"] and n.post:
        return redirect("posts:post_detail", pk=n.post.pk)

    if n.notification_type == "event" and n.event:
        return redirect("posts:event_detail", pk=n.event.pk)

    if n.notification_type == "follow":
        return redirect("profiles:profile", pk=n.sender.profile.pk)

    # Si no sabemos a dónde ir, al historial general
    return redirect("notifications:list")
