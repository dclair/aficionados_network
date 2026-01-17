"""
URL configuration for aficionados_network project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

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
    ContactView,
    LogoutView,
    ProfileView,
    ProfileUpdateView,
    ProfilesListView,
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
    path("contact/", ContactView.as_view(), name="contact"),
    path("profile/list/", ProfilesListView.as_view(), name="profile_list"),
    path("profile/<int:pk>", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]

# Configuración para servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
