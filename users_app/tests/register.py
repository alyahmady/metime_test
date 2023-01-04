from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users_app.otp import get_user_verification_code


class UserRegisterAPITestCase(APITestCase):
    def setUp(self):
        self.user_register_url = reverse("user-register")

    def test_success_register_api(self):
        response = self.client.post(
            self.user_register_url,
            {
                "first_name": "Aly",
                "last_name": "Ahmady",
                "phone": "+989050809253",
                "email": "test@gmail.com",
                "password": "HelloWorld1",
                "password_confirm": "HelloWorld1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

        self.assertTrue(response.data["is_active"])
        self.assertFalse(response.data["is_email_verified"])
        self.assertFalse(response.data["is_phone_verified"])

        # Assert verification code is sent and is set in cache (redis)
        code = get_user_verification_code(response.data["id"])
        self.assertIsInstance(code, str)
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), settings.VERIFICATION_CODE_DIGITS_COUNT)
