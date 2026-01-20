from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from aficionados_network.views import LoginView  # o donde tengas tu vista de login
from django.contrib.auth import views as auth_views

from .views import (
    HomeView,
    LoginView,
    RegisterView,
    LogoutView,
    ContactFormView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),  # Incluye las URLs de la app posts
    path(
        "profile/", include("profiles.urls")
    ),  # Esto delega las rutas a la app profiles
    path("", HomeView.as_view(), name="home"),
    # urls autenticación
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("contact/", ContactFormView.as_view(), name="contact"),
    path("pages/", include("django.contrib.flatpages.urls")),
    path("notifications/", include("notifications.urls")),
]

# Configuración para servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
