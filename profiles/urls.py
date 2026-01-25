# profiles/urls.py
from django.urls import path

from .views import (
    ProfilesListView,
    ProfileView,
    ProfileUpdateView,
    add_hobby,
    delete_hobby,
    add_review,
)

app_name = "profiles"

urlpatterns = [
    path("profile/list/", ProfilesListView.as_view(), name="profile_list"),
    path("profile/<int:pk>/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path("hobby/add/", add_hobby, name="add_hobby"),
    path("hobby/delete/<int:hobby_id>/", delete_hobby, name="delete_hobby"),
    path("review/add/<int:event_id>/", add_review, name="add_review"),
]
