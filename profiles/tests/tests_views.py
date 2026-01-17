from django.test import TestCase, override_settings
from profiles.models import UserProfile, Follow
from django.contrib.auth.models import User

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import shutil
import tempfile

# Crear un almacenamiento temporal para las pruebas
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestUserProfileViews(TestCase):
    @classmethod
    def tearDownClass(cls):
        # Limpiar el directorio temporal después de las pruebas
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            first_name="FirstTest",
            last_name="LastTest",
            email="testuser@example.com",
        )

        # PERFIL YA EXISTE POR SIGNAL
        self.user_profile = self.user.profile

        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpass2",
            email="testuser2@example.com",
        )

        self.user2_profile = self.user2.profile

        self.follow = Follow.objects.create(
            follower=self.user_profile, following=self.user2_profile
        )

    def test_profile_list_view(self):
        print("=== Probando la vista de lista de perfiles ===")

        # 1. Iniciar sesión
        self.client.login(username="testuser", password="testpass")
        # 2. Hacer la petición a la URL correcta
        response = self.client.get("/profile/list/")
        self.assertEqual(response.status_code, 200)
        # 3. Verificar que los usuarios están en el contexto
        self.assertIn("object_list", response.context)
        users_in_context = list(response.context["object_list"])

        # 4. Verificar que solo se devuelve el usuario que NO es el actual
        # (la vista excluye al usuario autenticado)
        self.assertEqual(len(users_in_context), 1)

        # 5. Verificar que el usuario devuelto es testuser2
        self.assertEqual(users_in_context[0].user.username, "testuser2")
        print("=== Prueba de vista de perfiles completada exitosamente ===")
