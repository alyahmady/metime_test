import time

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tokens import CustomRefreshToken
from metime.settings import UserIdentifierField
from users_app.models import CustomUser
from users_app.otp import get_user_verification_code, activation_key_generator


class OTPVerifyCodeAPITestCase(APITestCase):
    def setUp(self):
        self.otp_code_verify_url = reverse("otp-code-verify")
        self.resend_verification_code_url = reverse("resend-verification-code")

        self.user = CustomUser.objects.create_user(
            email="test12@gmail.com",
            password="HelloWorld1",
            is_email_verified=True,
            is_active=True,
        )

        refresh = CustomRefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token)
        )

    def test_successful_otp_code_verify_api(self):
        self.assertFalse(self.user.is_phone_verified)
        self.assertTrue(self.user.is_email_verified)

        self.user.is_email_verified = False
        self.user.save()

        self.assertTrue(self.user.is_active)

        # Generate new token, to test API permissions for active users (verified or not verified)
        refresh = CustomRefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token)
        )

        identifier = UserIdentifierField.EMAIL.value
        response = self.client.post(
            self.resend_verification_code_url,
            {
                "identifier_field": identifier,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("Verification code is sent", str(response.data["message"]))

        time.sleep(1)

        code = get_user_verification_code(
            user_id=self.user.pk, identifier_field=identifier
        )

        self.assertIsInstance(code, str)
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), settings.VERIFICATION_CODE_DIGITS_COUNT)

        response = self.client.post(
            self.otp_code_verify_url,
            {
                "code": code,
                "identifier_field": identifier,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("Account activated", str(response.data["message"]))

        self.user = CustomUser.objects.get(email=self.user.email)
        self.assertTrue(self.user.is_email_verified)

    def test_wrong_otp_code_verify_api(self):
        self.assertFalse(self.user.is_phone_verified)
        self.assertTrue(self.user.is_email_verified)

        self.user.is_email_verified = False
        self.user.save()

        self.assertTrue(self.user.is_active)

        # Generate new token, to test API permissions for active users (verified or not verified)
        refresh = CustomRefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token)
        )

        identifier = UserIdentifierField.EMAIL.value
        response = self.client.post(
            self.resend_verification_code_url,
            {
                "identifier_field": identifier,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("Verification code is sent", str(response.data["message"]))

        time.sleep(1)

        code = get_user_verification_code(
            user_id=self.user.pk, identifier_field=identifier
        )
        fake_code = activation_key_generator()
        while fake_code == code:
            fake_code = activation_key_generator()

        response = self.client.post(
            self.otp_code_verify_url,
            {
                "code": fake_code,
                "identifier_field": identifier,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("code is not valid", str(response.data["non_field_errors"]))

        self.user.is_email_verified = True
        self.user.save()
