import time

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from metime.settings import UserIdentifierField
from users_app.models import CustomUser
from users_app.otp import get_user_verification_code


class UserUpdateAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test12@gmail.com",
            phone="+989125467891",
            password="HelloWorld1",
            is_email_verified=True,
            is_phone_verified=True,
        )
        self.user_update_url = reverse("user-update", kwargs={"user_id": self.user.pk})
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token)
        )

    def test_success_update_api(self):
        self.user.is_email_verified = True
        self.user.is_phone_verified = True
        self.user.save()

        response = self.client.patch(
            path=self.user_update_url,
            data={
                "first_name": "Reza",
                "last_name": "Ahmady",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)
        self.assertIn("id", response.data)
        self.assertIn("date_joined", response.data)
        self.assertIn("is_active", response.data)
        self.assertIn("is_email_verified", response.data)
        self.assertIn("is_phone_verified", response.data)
        self.assertIn("phone", response.data)
        self.assertIn("email", response.data)

        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        self.assertEqual(response.data["first_name"], "Reza")
        self.assertEqual(response.data["last_name"], "Ahmady")

        self.assertTrue(response.data["is_active"])
        self.assertTrue(response.data["is_email_verified"])
        self.assertTrue(response.data["is_phone_verified"])

        self.user.is_email_verified = False
        self.user.is_phone_verified = False
        self.user.save()

    def test_verification_flag_after_identifier_update(self):
        self.user.is_email_verified = True
        self.user.is_phone_verified = True
        self.user.save()

        response = self.client.patch(
            path=self.user_update_url,
            data={
                "phone": "+989101397261",
            },
            format="json",
        )

        self.assertIn("phone", response.data)
        self.assertEqual(response.data["phone"], "+989101397261")

        self.assertIn("is_email_verified", response.data)
        self.assertIn("is_phone_verified", response.data)
        self.assertTrue(response.data["is_email_verified"])
        self.assertFalse(response.data["is_phone_verified"])

        # Assert verification code is sent for new phone and is set in cache (redis)

        time.sleep(1)

        self.assertIn("id", response.data)
        code = get_user_verification_code(
            user_id=response.data["id"], identifier_field=UserIdentifierField.PHONE
        )
        self.assertIsInstance(code, str)
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), settings.VERIFICATION_CODE_DIGITS_COUNT)
