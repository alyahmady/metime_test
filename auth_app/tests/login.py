import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from users_app.models import CustomUser


class LoginAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            phone="+989101397261", password="HelloWorld1"
        )
        self.user2 = CustomUser.objects.create_user(
            email="test@gmail.com", password="HelloWorld2"
        )

        self.token_obtain_pair_url = reverse("token-obtain-pair")
        self.token_refresh_url = reverse("token-refresh")

    def test_success_obtain_api(self):
        response1 = self.client.post(
            self.token_obtain_pair_url,
            {"phone": self.user1.phone.as_e164, "password": "HelloWorld1"},
            format="json",
        )
        response2 = self.client.post(
            self.token_obtain_pair_url,
            {"email": self.user2.email, "password": "HelloWorld2"},
            format="json",
        )

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertIn("access", response1.data)
        self.assertIn("refresh", response1.data)
        self.assertIn("access", response2.data)
        self.assertIn("refresh", response2.data)

    def test_extra_field_obtain_api(self):
        response = self.client.post(
            self.token_obtain_pair_url,
            {"email": self.user2.email, "hello": "world", "password": "HelloWorld2"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_missing_required_field_obtain_api(self):
        res1 = self.client.post(
            self.token_obtain_pair_url,
            {"password": "HelloWorld2"},
            format="json",
        )
        res2 = self.client.post(self.token_obtain_pair_url, {}, format="json")
        res3 = self.client.post(
            self.token_obtain_pair_url,
            {"email": self.user2.email},
            format="json",
        )
        res4 = self.client.post(
            self.token_obtain_pair_url,
            {"email": self.user1.phone.as_e164},
            format="json",
        )
        res5 = self.client.post(
            self.token_obtain_pair_url,
            {"hello": "world"},
            format="json",
        )

        for response in (res1, res2, res3, res4, res5):
            self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("non_field_errors", res1.data)
        self.assertIn("password", res2.data)
        self.assertIn("password", res3.data)
        self.assertIn("password", res4.data)
        self.assertIn("email", res4.data)
        self.assertIn("password", res5.data)

    def test_valid_access_token_obtain_api(self):
        response1 = self.client.post(
            self.token_obtain_pair_url,
            {"phone": self.user1.phone.as_e164, "password": "HelloWorld1"},
            format="json",
        )
        response2 = self.client.post(
            self.token_obtain_pair_url,
            {"email": self.user2.email, "password": "HelloWorld2"},
            format="json",
        )

        access1 = jwt.decode(
            response1.data["access"],
            settings.SIMPLE_JWT["SIGNING_KEY"],
            algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
        )
        access2 = jwt.decode(
            response2.data["access"],
            settings.SIMPLE_JWT["SIGNING_KEY"],
            algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
        )

        for auth_backend in settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]:
            auth_backend = import_string(auth_backend)
            auth_backend_worker = auth_backend()

            with self.assertRaisesMessage(AuthenticationFailed, "not verified"):
                auth_backend_worker.get_user(access1)

            with self.assertRaisesMessage(AuthenticationFailed, "not verified"):
                auth_backend_worker.get_user(access2)

            self.user1.is_verified = True
            self.user1.save()
            self.user2.is_verified = True
            self.user2.save()

            user1 = auth_backend_worker.get_user(access1)
            user2 = auth_backend_worker.get_user(access2)

            self.assertIsNotNone(user1, None)
            self.assertIsNotNone(user2, None)

            self.assertIsInstance(user1, get_user_model())
            self.assertIsInstance(user2, get_user_model())

            self.user1.is_verified = False
            self.user1.save()
            self.user2.is_verified = False
            self.user2.save()

    def test_valid_refresh_token_obtain_api(self):
        response1 = self.client.post(
            self.token_obtain_pair_url,
            {"phone": self.user1.phone.as_e164, "password": "HelloWorld1"},
            format="json",
        )
        response2 = self.client.post(
            self.token_obtain_pair_url,
            {"email": self.user2.email, "password": "HelloWorld2"},
            format="json",
        )

        refresh1 = response1.data["refresh"]
        refresh2 = response2.data["refresh"]

        refresh_response1 = self.client.post(
            self.token_refresh_url,
            {"refresh": refresh1},
            format="json",
        )
        refresh_response2 = self.client.post(
            self.token_refresh_url,
            {"refresh": refresh2},
            format="json",
        )

        self.assertEqual(refresh_response1.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh_response2.status_code, status.HTTP_200_OK)

        self.assertIn("access", refresh_response1.data)
        self.assertIn("refresh", refresh_response1.data)
        self.assertIn("access", refresh_response2.data)
        self.assertIn("refresh", refresh_response2.data)

        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False) is True:
            self.assertNotEqual(refresh_response1.data["refresh"], refresh1)
            self.assertNotEqual(refresh_response2.data["refresh"], refresh2)

    def test_extra_field_refresh_api(self):
        access_response = self.client.post(
            self.token_obtain_pair_url,
            {"phone": self.user1.phone.as_e164, "password": "HelloWorld1"},
            format="json",
        )
        response = self.client.post(
            self.token_refresh_url,
            {"refresh": access_response.data["refresh"], "hello": "world"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_missing_required_field_refresh_api(self):
        response = self.client.post(self.token_refresh_url, {}, format="json")

        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)

    def test_inactive_user_token_obtain_error(self):
        self.user1.is_active = False
        self.user1.save()

        response = self.client.post(
            self.token_obtain_pair_url,
            {"phone": self.user1.phone.as_e164, "password": "HelloWorld1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.user1.is_active = True
        self.user1.save()