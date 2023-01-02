from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

from metime.settings import UserIdentifierField
from users_app.models import CustomUser
from users_app.verification import activation_key_generator, send_user_verification_code, send_user_reset_password_code


class VerificationTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(phone="+989101397261", password="HelloWorld1")
        CustomUser.objects.create_user(email="test@gmail.com", password="Helloworld2")

    def test_activation_code_generator(self):
        code = activation_key_generator()
        self.assertIsInstance(code, str)
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), settings.VERIFICATION_CODE_DIGITS_COUNT)

    def test_error_on_verifying_verified_user(self):
        user = CustomUser.objects.get(phone="+989101397261")
        user.is_verified = True
        user.save()

        with self.assertRaisesMessage(ValueError, "already verified"):
            send_user_verification_code(user=user, user_field=UserIdentifierField.PHONE)

    def test_verification_code_in_cache_existence(self):
        user1 = CustomUser.objects.get(phone="+989101397261")
        user2 = CustomUser.objects.get(email="test@gmail.com")
        user1.is_verified = False
        user2.is_verified = False
        user1.save()
        user2.save()

        send_user_verification_code(user=user1, user_field=UserIdentifierField.PHONE)
        send_user_verification_code(user=user2, user_field=UserIdentifierField.EMAIL)

        code1 = cache.get(
            key=settings.VERIFICATION_CACHE_KEY.format(str(user1.id)),
        )
        code2 = cache.get(
            key=settings.VERIFICATION_CACHE_KEY.format(str(user2.id)),
        )

        self.assertIsInstance(code1, str)
        self.assertTrue(code1.isdigit())
        self.assertEqual(len(code1), settings.VERIFICATION_CODE_DIGITS_COUNT)

        self.assertIsInstance(code2, str)
        self.assertTrue(code2.isdigit())
        self.assertEqual(len(code2), settings.VERIFICATION_CODE_DIGITS_COUNT)

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
