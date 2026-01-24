from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import UserProfile, Follow, Hobby, UserHobby


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user_username", "user_email", "location_short", "created_at"]
    list_display_links = ["user_username", "user_email"]
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "bio",
        "location",
    ]
    list_filter = ["location", "created_at", "updated_at"]
    list_per_page = 20
    readonly_fields = ["created_at", "updated_at", "profile_picture_preview"]
    fieldsets = (
        (
            "Información del Usuario",
            {"fields": ("user", "profile_picture", "profile_picture_preview")},
        ),
        (
            "Información Personal",
            {"fields": ("bio", "birth_date", "location", "website")},
        ),
        (
            "Metadatos",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def user_username(self, obj):
        # Enlace al perfil del usuario en lugar de al formulario de autenticación
        url = reverse("admin:profiles_userprofile_change", args=[obj.id])
        return format_html(
            '{} <small class="text-muted">(ID: {})</small>',
            format_html('<a href="{}">{}</a>', url, obj.user.username),
            obj.user.id,
        )

    user_username.short_description = "Usuario"
    user_username.admin_order_field = "user__username"

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Email"
    user_email.admin_order_field = "user__email"

    def location_short(self, obj):
        return (
            obj.location[:30] + "..."
            if obj.location and len(obj.location) > 30
            else obj.location or "-"
        )

    location_short.short_description = "Ubicación"
    location_short.admin_order_field = "location"

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.profile_picture.url,
            )
        return "(Sin imagen)"

    profile_picture_preview.short_description = "Vista previa"

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            # Si es un número, busca por ID
            if search_term.isdigit():
                queryset = self.model.objects.filter(pk=search_term) | queryset
            # Busca por username exacto
            queryset = (
                self.model.objects.filter(user__username__iexact=search_term) | queryset
            )
        return queryset, use_distinct


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["follower_username", "following_username", "created_at"]
    search_fields = [
        "follower__user__username",
        "following__user__username",
        "follower__user__email",
        "following__user__email",
    ]
    list_filter = ["created_at"]
    date_hierarchy = "created_at"

    def follower_username(self, obj):
        url = reverse("admin:profiles_userprofile_change", args=[obj.follower.id])
        return format_html('<a href="{}">{}</a>', url, obj.follower.user.username)

    follower_username.short_description = "Seguidor"
    follower_username.admin_order_field = "follower__user__username"

    def following_username(self, obj):
        url = reverse("admin:profiles_userprofile_change", args=[obj.following.id])
        return format_html('<a href="{}">{}</a>', url, obj.following.user.username)

    following_username.short_description = "Siguiendo a"
    following_username.admin_order_field = "following__user__username"


@admin.register(Hobby)
class HobyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")


@admin.register(UserHobby)
class UserHobbyAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "hobby")
    search_fields = ("profile__user__username", "hobby__name")
    list_filter = ("hobby", "profile")
