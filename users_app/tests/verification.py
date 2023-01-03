import time

from django.conf import settings
from django.test import TestCase

from users_app.models import CustomUser
from users_app.otp import (
    activation_key_generator,
    send_user_verification_code,
    get_user_verification_code,
)


class CustomUserVerificationTestCase(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            phone="+989101397261", password="HelloWorld1", is_verified=False
        )
        self.user2 = CustomUser.objects.create_user(
            email="test@gmail.com", password="Helloworld2", is_verified=False
        )

    def test_activation_code_generator(self):
        code = activation_key_generator()
        self.assertIsInstance(code, str)
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), settings.VERIFICATION_CODE_DIGITS_COUNT)

    def test_error_on_verifying_verified_user(self):
        self.user1.is_verified = True
        self.user1.save()

        self.user2.is_verified = True
        self.user2.save()

        with self.assertRaisesMessage(ValueError, "already verified"):
            send_user_verification_code(
                is_verified=self.user1.is_verified,
                user_id=self.user1.pk,
                user_identifier=self.user1.phone,
            )
        with self.assertRaisesMessage(ValueError, "already verified"):
            send_user_verification_code(
                is_verified=self.user2.is_verified,
                user_id=self.user2.pk,
                user_identifier=self.user2.phone,
            )

        self.user1.is_verified = False
        self.user1.save()

        self.user2.is_verified = False
        self.user2.save()

    def test_verification_code_in_cache_existence(self):
        self.assertFalse(self.user1.is_verified)
        self.assertFalse(self.user2.is_verified)

        send_user_verification_code(
            is_verified=self.user1.is_verified,
            user_id=self.user1.pk,
            user_identifier=self.user1.phone,
        )
        send_user_verification_code(
            is_verified=self.user2.is_verified,
            user_id=self.user2.pk,
            user_identifier=self.user2.email,
        )

        code1 = get_user_verification_code(self.user1.pk)
        code2 = get_user_verification_code(self.user2.pk)

        self.assertIsInstance(code1, str)
        self.assertTrue(code1.isdigit())
        self.assertEqual(len(code1), settings.VERIFICATION_CODE_DIGITS_COUNT)

        self.assertIsInstance(code2, str)
        self.assertTrue(code2.isdigit())
        self.assertEqual(len(code2), settings.VERIFICATION_CODE_DIGITS_COUNT)


    def test_async_verification_code_in_cache_existence(self):
        self.assertFalse(self.user1.is_verified)
        self.assertFalse(self.user2.is_verified)

        task1 = send_user_verification_code.apply_async(kwargs={
            "is_verified": self.user1.is_verified,
            "user_id": self.user1.pk,
            "user_identifier": self.user1.phone.as_e164,
        })
        task2 = send_user_verification_code.apply_async(kwargs={
            "is_verified": self.user2.is_verified,
            "user_id": self.user2.pk,
            "user_identifier": self.user2.email,
        })

        time.sleep(2)

        if settings.DEBUG:
            self.assertEqual(task1.status, "SUCCESS")
            self.assertEqual(task2.status, "SUCCESS")
        else:
            self.assertEqual(task1.status, "PENDING")
            self.assertEqual(task2.status, "PENDING")

        code1 = get_user_verification_code(self.user1.pk)
        code2 = get_user_verification_code(self.user2.pk)

        self.assertIsInstance(code1, str)
        self.assertTrue(code1.isdigit())
        self.assertEqual(len(code1), settings.VERIFICATION_CODE_DIGITS_COUNT)

        self.assertIsInstance(code2, str)
        self.assertTrue(code2.isdigit())
        self.assertEqual(len(code2), settings.VERIFICATION_CODE_DIGITS_COUNT)

    def test_verification_status_after_identifier_change(self):
        self.assertFalse(self.user1.is_verified)
        self.assertFalse(self.user2.is_verified)

        self.user1.is_verified = True
        self.user2.is_verified = True
        self.user1.save()
        self.user2.save()
        self.assertTrue(self.user1.is_verified)
        self.assertTrue(self.user2.is_verified)

        self.user1.phone = "+989127072456"
        self.user2.email = "test78@gmail.com"
        self.user1.save()
        self.user2.save()
        self.assertFalse(self.user1.is_verified)
        self.assertFalse(self.user2.is_verified)

        self.user1.is_verified = True
        self.user2.is_verified = True
        self.user1.save()
        self.user2.save()
        self.assertTrue(self.user1.is_verified)
        self.assertTrue(self.user2.is_verified)

        self.user1.email = "test79@gmail.com"
        self.user2.phone = "+989127072457"
        self.user1.save()
        self.user2.save()
        self.assertFalse(self.user1.is_verified)
        self.assertFalse(self.user2.is_verified)
