from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class TestCoreViews(TestCase):
    def test_home_view(self):
        print("=== Probando vista home ===")
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        print("=== Vista home probada exitosamente ===")
