from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    # Tu vista de lista (la que es una clase)
    path("", views.NotificationListView.as_view(), name="list"),
    # LA CORRECCIÓN: Quita "NotificationListView." de aquí
    path("read/<int:pk>/", views.notification_redirect, name="notification_redirect"),
]
