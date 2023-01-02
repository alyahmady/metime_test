from django.db import DatabaseError
from django.test import TestCase

from users_app.models import CustomUser


class CustomUserTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(phone="+989101397261", password="HelloWorld1")
        CustomUser.objects.create_user(email="test@gmail.com", password="Helloworld2")
        CustomUser.objects.create_user(
            email="test2@gmail.com",
            password="Helloworld3",
            first_name="Amir",
            last_name="Ahmady",
        )
        CustomUser.objects.create_user(
            phone="+989050809253",
            password="HelloWorld4",
            first_name="Aly",
            last_name="Ahmady",
        )

    def test_attributes_after_creation(self):
        user = CustomUser.objects.create_superuser(
            email="admin@gmail.com", password="HelloWorld4"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

        user = CustomUser.objects.create_user(
            email="normal.user@gmail.com", password="HelloWorld4"
        )
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_verified)
        self.assertTrue(user.is_active)

    def test_getting_by_identifier(self):
        user = CustomUser.objects.get_by_natural_key("+989050809253")
        self.assertTrue(user.check_password("HelloWorld4"))
        self.assertEqual(user.first_name, "Aly")
        self.assertEqual(user.last_name, "Ahmady")

        user = CustomUser.objects.get_by_natural_key("test@gmail.com")
        self.assertTrue(user.check_password("Helloworld2"))

        user = CustomUser.objects.get_by_phone("+989101397261")
        self.assertTrue(user.check_password("HelloWorld1"))

        user = CustomUser.objects.get_by_email("test2@gmail.com")
        self.assertTrue(user.check_password("Helloworld3"))
        self.assertEqual(user.first_name, "Amir")
        self.assertEqual(user.last_name, "Ahmady")

    def test_bad_arguments_object_creation(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create(phone="+989050809254")

        with self.assertRaises(ValueError):
            CustomUser.objects.create(email="hello@gmail.com")

        with self.assertRaises(ValueError):
            CustomUser.objects.create(password="helloworld")

        with self.assertRaises(ValueError):
            CustomUser.objects.create(first_name="Aly", last_name="Ahmady")

        with self.assertRaises(TypeError):
            # Correct arguments with one non-related field
            CustomUser.objects.create(
                email="hello3@gmail.com", password="goodday", not_related_field="abc"
            )

    def test_error_on_duplicate_identifiers(self):
        with self.assertRaises(DatabaseError):
            CustomUser.objects.create_user(
                phone="+989101397261", password="new_password"
            )

        with self.assertRaises(DatabaseError):
            CustomUser.objects.create_user(
                email="test@gmail.com", password="helloworld2"
            )
