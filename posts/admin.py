from django.contrib import admin
from .models import Posts, Comment, Event


# Register your models here.
@admin.register(Posts)
class PostsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "image", "caption", "created_at", "updated_at")
    list_display_links = ("id", "user", "image", "caption", "created_at", "updated_at")
    list_filter = ("user", "created_at", "updated_at")
    search_fields = ("user__username", "caption")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "comment", "created_at", "updated_at")
    list_display_links = ("id", "user", "post", "comment", "created_at", "updated_at")
    list_filter = ("user", "post", "created_at", "updated_at")
    search_fields = ("user__username", "post__title")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "hobby",
        "event_date",
        "organizer",
        "is_canceled",
        "created_at",
    )
    list_display_links = ("id", "title", "hobby", "event_date", "organizer")
    list_filter = ("is_canceled", "hobby", "event_date", "created_at")
    search_fields = ("title", "hobby", "is_canceled", "organizer__username")
