from django.test import TestCase
from profiles.models import UserProfile, Follow, User
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError


class UserProfileTestCase(TestCase):

    def setUp(self):

        # 1. Crear usuarios primero
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="testuser2@example.com", password="testpass"
        )

        # 2. Obtener los perfiles (deberían crearse automáticamente por la señal)
        self.user_profile = self.user.profile
        self.user_profile2 = self.user2.profile

        # 3. Actualizar los perfiles si es necesario
        self.user_profile.bio = "pintor"
        self.user_profile.website = "https://test.com"
        self.user_profile.save()

        self.user_profile2.bio = "musico"
        self.user_profile2.website = "https://test2.com"
        self.user_profile2.save()

        # 4. Crear la relación de seguimiento
        self.follow = Follow.objects.create(
            follower=self.user_profile,  # Quién sigue
            following=self.user_profile2,  # A quién se sigue
        )

    def test_user_profile_creation(self):
        print("=== Probando creación de perfil ===")
        self.assertEqual(self.user_profile.bio, "pintor")
        self.assertEqual(self.user_profile.user.username, "testuser")

    def test_follow_relationship(self):
        print("=== Probando relación de seguimiento ===")
        # Verifica que la relación de seguimiento se creó correctamente
        self.assertEqual(self.follow.follower, self.user_profile)
        self.assertEqual(self.follow.following, self.user_profile2)
        self.assertEqual(
            list(self.user_profile.following_relationships.all()), [self.follow]
        )
        self.assertEqual(
            list(self.user_profile2.follower_relationships.all()), [self.follow]
        )

    def test_follow_user(self):
        print("=== Probando seguir usuario ===")
        # Verifica que un usuario puede seguir a otro
        # Asegurarse de que no exista una relación previa
        Follow.objects.filter(
            follower=self.user_profile, following=self.user_profile2
        ).delete()

        # Crear la relación de seguimiento
        follow = Follow.objects.create(
            follower=self.user_profile, following=self.user_profile2
        )

        # Verificar que la relación existe
        self.assertTrue(
            Follow.objects.filter(
                follower=self.user_profile, following=self.user_profile2
            ).exists()
        )

        # Verificar las relaciones inversas
        self.assertIn(follow, self.user_profile.following_relationships.all())
        self.assertIn(follow, self.user_profile2.follower_relationships.all())

    def test_unfollow_user(self):
        print("=== Probando dejar de seguir usuario ===")
        # Verifica que un usuario puede dejar de seguir a otro
        # Asegurarse de que no exista una relación previa
        Follow.objects.filter(
            follower=self.user_profile, following=self.user_profile2
        ).delete()

        # Crear la relación de seguimiento
        follow = Follow.objects.create(
            follower=self.user_profile, following=self.user_profile2
        )

        # Verificar que la relación existe antes de eliminarla
        self.assertTrue(
            Follow.objects.filter(
                follower=self.user_profile, following=self.user_profile2
            ).exists()
        )

        # Eliminar la relación de seguimiento
        follow.delete()

        # Verificar que la relación ya no existe
        self.assertFalse(
            Follow.objects.filter(
                follower=self.user_profile, following=self.user_profile2
            ).exists()
        )

        # Verificar que se eliminó de las relaciones inversas
        with self.assertRaises(Follow.DoesNotExist):
            Follow.objects.get(follower=self.user_profile, following=self.user_profile2)

    def test_str_userprofile(self):
        print("=== Probando método __str__ de UserProfile ===")
        # Verifica que el método __str__ de UserProfile devuelve el username
        self.assertEqual(str(self.user_profile), self.user.username)


class FollowTestCase(TestCase):
    def setUp(self):
        print("=== Iniciando setUp de FollowTestCase ===")
        # 1. Crear usuarios primero
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="testuser2@example.com", password="testpass"
        )

        # 2. Obtener los perfiles (deberían crearse automáticamente por la señal)
        self.user_profile = self.user.profile
        self.user_profile2 = self.user2.profile

        # 3. Actualizar los perfiles si es necesario
        self.user_profile.bio = "pintor"
        self.user_profile.website = "https://test.com"
        self.user_profile.save()

        self.user_profile2.bio = "musico"
        self.user_profile2.website = "https://test2.com"
        self.user_profile2.save()

        # 4. Crear la relación de seguimiento
        self.follow = Follow.objects.create(
            follower=self.user_profile, following=self.user_profile2
        )

    def test_follow_creation(self):
        print("=== Probando creación de relación de seguimiento ===")
        # Verifica que la relación de seguimiento se creó correctamente
        self.assertEqual(self.follow.follower, self.user_profile)
        self.assertEqual(self.follow.following, self.user_profile2)

    def test_follow_relationships(self):
        print("=== Probando relaciones de seguimiento ===")
        # Verifica las relaciones de seguimiento
        self.assertIn(self.follow, self.user_profile.following_relationships.all())
        self.assertIn(self.follow, self.user_profile2.follower_relationships.all())

    def test_follow_count(self):
        print("=== Probando conteo de seguidores y seguidos ===")
        # Verifica el conteo de seguidores y seguidos
        self.assertEqual(self.user_profile.following_count(), 1)
        self.assertEqual(
            self.user_profile2.followers_count(), 1
        )  # followers_count en plural

    def test_unfollow(self):
        print("=== Probando dejar de seguir ===")
        # Verifica que se puede eliminar la relación de seguimiento
        follow_id = self.follow.id
        self.follow.delete()

        # Verifica que la relación fue eliminada
        with self.assertRaises(Follow.DoesNotExist):
            Follow.objects.get(id=follow_id)

    def test_str_follow(self):
        print("=== Probando método __str__ de Follow ===")
        # Verifica que el método __str__ de Follow devuelve la relación correcta
        self.assertEqual(
            str(self.follow),
            f"{self.user_profile.user.username} follows {self.user_profile2.user.username}",
        )

    def test_unique_follow_relationship(self):
        print("=== Probando relación de seguimiento única ===")
        # Verificar que la relación ya existe
        self.assertTrue(
            Follow.objects.filter(
                follower=self.user_profile, following=self.user_profile2
            ).exists()
        )

        # Contar relaciones existentes
        initial_count = Follow.objects.count()

        # Intentar crear una relación duplicada
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Follow.objects.create(
                    follower=self.user_profile, following=self.user_profile2
                )

        # Verificar que no se crearon nuevas relaciones
        self.assertEqual(Follow.objects.count(), initial_count)

        # Verificar que solo existe una relación
        self.assertEqual(
            Follow.objects.filter(
                follower=self.user_profile, following=self.user_profile2
            ).count(),
            1,
        )
