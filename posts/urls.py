from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("create/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("like/", views.toggle_like, name="toggle_like"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/new/", views.EventCreateView.as_view(), name="event_create"),
    path(
        "events/<int:event_id>/toggle/",
        views.toggle_attendance,
        name="toggle_attendance",
    ),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("event/<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_update"),
    path(
        "event/<int:pk>/cancel/", views.EventCancelView.as_view(), name="event_cancel"
    ),
    path(
        "event/<int:event_id>/comment/",
        views.add_event_comment,
        name="add_event_comment",
    ),
    path("my-events/", views.MyEventsListView.as_view(), name="my_events"),
    path(
        "event/<int:pk>/reactivate/",
        views.EventReactivateView.as_view(),
        name="event_reactivate",
    ),
]
