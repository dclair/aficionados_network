from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from aficionados_network.views import LoginView  # o donde tengas tu vista de login
from django.contrib.auth import views as auth_views

from .views import (
    HomeView,
    LegalView,
    LoginView,
    RegisterView,
    LogoutView,
    ProfileView,
    ProfileUpdateView,
    ProfilesListView,
    ContactFormView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),  # Incluye las URLs de la app posts
    path("", HomeView.as_view(), name="home"),
    path("legal/", LegalView.as_view(), name="legal"),
    # urls autenticación
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/list/", ProfilesListView.as_view(), name="profile_list"),
    path("profile/<int:pk>", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path("contact/", ContactFormView.as_view(), name="contact"),
]

# Configuración para servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
