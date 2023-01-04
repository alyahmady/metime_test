import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users_app.models import CustomUser


class UserChangePasswordAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test13@gmail.com",
            password="HelloWorld1",
            is_email_verified=True,
        )

        self.change_password_url = reverse(
            "user-password-change", kwargs={"user_id": self.user.pk}
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token)
        )

    def test_success_update_api(self):
        self.assertTrue(self.user.check_password("HelloWorld1"))

        today = timezone.now().date()

        response = self.client.put(
            path=self.change_password_url,
            data={
                "current_password": "HelloWorld1",
                "new_password": "HelloWorld2",
                "new_password_confirm": "HelloWorld2",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user = CustomUser.objects.get(email="test13@gmail.com")
        self.assertTrue(self.user.check_password("HelloWorld2"))

        self.assertIsNotNone(self.user.last_password_change)
        self.assertIsInstance(self.user.last_password_change, datetime.datetime)
        self.assertEqual(self.user.last_password_change.date(), today)
