# profiles/urls.py
from django.urls import path

from .views import ProfilesListView, ProfileView, ProfileUpdateView

app_name = "profiles"

urlpatterns = [
    path("profile/list/", ProfilesListView.as_view(), name="profile_list"),
    path("profile/<int:pk>/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]
