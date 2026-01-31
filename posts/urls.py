from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    # rutas para los posts
    path("create/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("post/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    # rutas para los eventos
    path("", views.EventListView.as_view(), name="event_list"),
    path("new/", views.EventCreateView.as_view(), name="event_create"),
    path(
        "<int:event_id>/toggle/",
        views.toggle_attendance,
        name="toggle_attendance",
    ),
    path("<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_update"),
    path("<int:pk>/cancel/", views.EventCancelView.as_view(), name="event_cancel"),
    path(
        "<int:event_id>/comment/",
        views.add_event_comment,
        name="add_event_comment",
    ),
    # rutas para los eventos del usuario
    path("my-events/", views.MyEventsListView.as_view(), name="my_events"),
    path(
        "event/<int:pk>/reactivate/",
        views.EventReactivateView.as_view(),
        name="event_reactivate",
    ),
    path("event/<int:pk>/duplicate/", views.duplicate_event, name="event_duplicate"),
    # rutas para las inscripciones del usuario
    path(
        "mis-inscripciones/",
        views.MyParticipationsListView.as_view(),
        name="my_participations",
    ),
    # rutas para los planes organizados por el usuario
    path("mis-planes-organizados/", views.MyEventsListView.as_view(), name="my_events"),
]
