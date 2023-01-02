from typing import Tuple

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python, PhoneNumber

from metime.settings import UserIdentifierField


class CustomUserManager(UserManager):
    def create(self, *args, **kwargs):
        self.create_user(*args, **kwargs)

    def create_user(self, phone=None, email=None, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_verified", False)
        extra_fields.setdefault("is_active", True)

        if not email and not phone:
            raise ValueError(_("Either Email or Phone must be set"))

        if not password:
            raise ValueError(_("User creation without setting password is not allowed"))

        if email:
            email = self.normalize_email(email)

        user = self.model(email=email, phone=phone, **extra_fields)
        validate_password(password)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields["is_superuser"] = True
        extra_fields["is_staff"] = True
        extra_fields["is_verified"] = True
        extra_fields["is_active"] = True

        return self.create_user(email=email, password=password, **extra_fields)

    def get_by_natural_key(self, user_identifier):
        field_name, validated_value = self.model.get_user_identifier_field(
            user_identifier
        )
        match field_name:
            case UserIdentifierField.EMAIL:
                return self.get_by_email(email=validated_value)
            case UserIdentifierField.PHONE:
                return self.get_by_phone(phone=validated_value)

    def get_by_email(self, email):
        case_insensitive_email_field = "{}__iexact".format(self.model.EMAIL_FIELD)
        return self.get(**{case_insensitive_email_field: email})

    def get_by_phone(self, phone):
        try:
            phone = to_python(phone)
            if phone:
                return self.get(phone=phone)
        except:
            pass


class CustomUser(AbstractUser):
    username = None
    create_date = None

    # Datetime fields
    last_password_change = models.DateTimeField(
        _("Last Password Change"), null=True, default=None
    )

    # Profile data fields
    first_name = models.CharField(_("First Name"), max_length=50, null=True)
    last_name = models.CharField(_("Last Name"), max_length=100, null=True)

    # Necessary fields
    phone = PhoneNumberField(
        _("Phone Number"),
        unique=True,
        null=True,
        error_messages={
            "unique": _("A User with that Phone number already exists."),
        },
    )
    email = models.EmailField(
        _("Email Address"),
        unique=True,
        null=True,
        error_messages={
            "unique": _("A User with that Email already exists."),
        },
    )
    __original_phone = None
    __original_email = None

    # Flag fields
    is_verified = models.BooleanField(_("Is Verified"), default=False)
    is_active = models.BooleanField(_("Is Active"), default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    EMAIL_FIELD = "email"
    PHONE_FIELD = "phone"

    objects = CustomUserManager()

    @property
    def full_name(self):
        return " ".join([self.first_name or "", self.last_name or ""]).strip()

    class Meta:
        app_label = "users_app"
        db_table = "metime_users"
        ordering = ["-date_joined"]
        default_related_name = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        constraints = [
            models.CheckConstraint(
                check=Q(phone__isnull=False) | Q(email__isnull=False),
                name="email_phone_null",
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # To keep last values before calling super().save() -> to detect updates without DB call
        self.__original_phone = self.phone
        self.__original_email = self.email

    def save(self, *args, **kwargs):
        password_changed = False
        if self._password is not None:
            password_changed = True

        if self.phone != self.__original_phone or self.email != self.__original_email:
            self.is_verified = False

        super().save(*args, **kwargs)

        self.__original_email = self.email
        self.__original_phone = self.phone

        if password_changed:
            self.last_password_change = timezone.now()

    def __str__(self):
        return f"{self.full_name or self.id}"

    @classmethod
    def get_user_identifier_field(
        cls, user_identifier
    ) -> Tuple[UserIdentifierField, PhoneNumber | str]:
        try:
            phone = to_python(user_identifier)
            if not isinstance(phone, PhoneNumber):
                raise ValidationError(
                    _("The phone number entered is not valid."),
                    code="invalid_phone_number",
                )
            if not phone.is_valid():
                raise ValidationError(
                    _("The phone number entered is not valid."),
                    code="invalid_phone_number",
                )
            return UserIdentifierField.PHONE, phone
        except:
            try:
                validate_email(user_identifier)
                return (
                    UserIdentifierField.EMAIL,
                    cls._default_manager.normalize_email(user_identifier),
                )
            except:
                raise ValueError(
                    "Invalid identifier value. Either must be email or phone number"
                )

    def sms_user(self, message, from_number=None, **kwargs):
        # TODO -> Not implemented yet
        print(message)
