from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        (1, _("Male")),
        (2, _("Female")),
        (3, _("Other")),
    ]

    username = None
    create_date = None

    # Profile data fields
    first_name = models.CharField(_("First Name"), max_length=50, null=True)
    last_name = models.CharField(_("Last Name"), max_length=100, null=True)

    # Necessary fields
    phone = PhoneNumberField(
        _("Phone Number"),
        unique=True,
        null=True,
        error_messages={
            'unique': _("A User with that Phone number already exists."),
        },
    )
    email = models.EmailField(
        _("Email Address"),
        unique=True,
        null=True,
        error_messages={
            'unique': _("A User with that Email already exists."),
        },
    )
    is_email_verified = models.BooleanField(_('Is Email Verified'), default=False)

    is_active = models.BooleanField(_("Is Active"), default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    EMAIL_FIELD = 'email'

    @property
    def full_name(self):
        return ' '.join([self.first_name or "", self.last_name or ""]).strip()

    class Meta:
        app_label = 'users_app'
        db_table = 'metime_users'
        ordering = ['-date_joined']
        default_related_name = 'users'
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        constraints = [
            models.CheckConstraint(
                check=Q(phone__isnull=False) | Q(email__isnull=False),
                name='email_phone_null'
            )
        ]

    def __str__(self):
        return f"{self.full_name or self.id}"
