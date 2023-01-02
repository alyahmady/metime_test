import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from metime.settings import UserIdentifierField
from users_app.models import CustomUser
from users_app.otp import (
    send_user_reset_password_code,
)


class CustomUserPasswordTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(phone="+989101397261", password="HelloWorld1")
        CustomUser.objects.create_user(email="test@gmail.com", password="HelloWorld2")

    def test_bad_password(self):
        with self.assertRaisesMessage(ValidationError, "too common"):
            CustomUser.objects.create_user(
                email="better.aly.ahmady@gmail.com", password="helloworld"
            )

        with self.assertRaisesMessage(ValidationError, "entirely numeric"):
            CustomUser.objects.create_user(
                email="better.aly.ahmady2@gmail.com", password="1234123489765"
            )

        with self.assertRaisesMessage(ValidationError, "too short"):
            CustomUser.objects.create_user(
                email="better.aly.ahmady3@gmail.com", password="ab123"
            )

    def test_password_check(self):
        user1 = CustomUser.objects.get(phone="+989101397261")
        user2 = CustomUser.objects.get(email="test@gmail.com")

        self.assertTrue(user1.check_password("HelloWorld1"))
        self.assertTrue(user2.check_password("HelloWorld2"))

    def test_password_setting(self):
        user1 = CustomUser.objects.get(phone="+989101397261")
        user2 = CustomUser.objects.get(email="test@gmail.com")

        user1.set_password("HelloWorld123!@#")
        user1.save()
        user2.set_password("HelloWorld456$%^")
        user2.save()

        self.assertTrue(user1.check_password("HelloWorld123!@#"))
        self.assertTrue(user2.check_password("HelloWorld456$%^"))

        user1.set_password("HelloWorld1")
        user1.save()
        user2.set_password("HelloWorld2")
        user2.save()

    def test_password_change(self):
        user1 = CustomUser.objects.get(phone="+989101397261")
        user2 = CustomUser.objects.get(email="test@gmail.com")

        today = timezone.now().date()

        user1.set_password("HelloWorld123!@#")
        user1.save()
        user2.set_password("HelloWorld456$%^")
        user2.save()

        self.assertIsNotNone(user1.last_password_change)
        self.assertIsInstance(user1.last_password_change, datetime.datetime)
        self.assertIsNotNone(user2.last_password_change)
        self.assertIsInstance(user2.last_password_change, datetime.datetime)

        self.assertEqual(user1.last_password_change.date(), today)
        self.assertEqual(user2.last_password_change.date(), today)

        self.assertTrue(user1.check_password("HelloWorld123!@#"))
        self.assertTrue(user2.check_password("HelloWorld456$%^"))

        user1.set_password("HelloWorld1")
        user1.save()
        user2.set_password("HelloWorld2")
        user2.save()

    def test_reset_password_code_in_cache_existence(self):
        user1 = CustomUser.objects.get(phone="+989101397261")
        user2 = CustomUser.objects.get(email="test@gmail.com")
        user1.is_verified = False
        user2.is_verified = False
        user1.save()
        user2.save()

        send_user_reset_password_code(user=user1, user_field=UserIdentifierField.PHONE)
        send_user_reset_password_code(user=user2, user_field=UserIdentifierField.EMAIL)

        code1 = cache.get(
            key=settings.RESET_PASSWORD_CACHE_KEY.format(str(user1.id)),
        )
        code2 = cache.get(
            key=settings.RESET_PASSWORD_CACHE_KEY.format(str(user2.id)),
        )

        self.assertIsInstance(code1, str)
        self.assertTrue(code1.isdigit())
        self.assertEqual(len(code1), settings.VERIFICATION_CODE_DIGITS_COUNT)

        self.assertIsInstance(code2, str)
        self.assertTrue(code2.isdigit())
        self.assertEqual(len(code2), settings.VERIFICATION_CODE_DIGITS_COUNT)
