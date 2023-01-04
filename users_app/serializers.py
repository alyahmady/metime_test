from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from metime.settings import UserIdentifierField
from users_app.models import CustomUser
from users_app.otp import (
    send_user_verification_code,
    get_user_verification_code,
    delete_user_verification_code,
)


class UserSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(required=False, allow_null=False)
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "date_joined",
            "first_name",
            "last_name",
            "phone",
            "email",
            "password",
            "password_confirm",
            "is_active",
            "is_phone_verified",
            "is_email_verified",
        )
        read_only_fields = (
            "id",
            "date_joined",
            "is_active",
            "is_phone_verified",
            "is_email_verified",
        )
        extra_kwargs = {
            "email": {"required": False, "allow_null": False},
        }

    def _user_verification_process(self, user: CustomUser):
        verification_kwargs = user.get_verification_kwargs()
        if not user.is_verified and verification_kwargs:
            send_user_verification_code.apply_async(kwargs=verification_kwargs)

    def validate(self, data):
        data = super(UserSerializer, self).validate(data)
        if "password" in data:
            password = data.get("password")
            try:
                password_confirm = data.pop("password_confirm")
                assert password == password_confirm
            except (AssertionError, LookupError):
                raise ValidationError("Passwords doesn't match")
            validate_password(password)
        return data

    def create(self, validated_data):
        data = validated_data.copy()

        if "email" not in data and "phone" not in data:
            raise ValidationError(
                "Either `phone` or `email` fields must be in the request payload"
            )

        try:
            password = data.pop("password")
        except LookupError:
            raise ValidationError(f"`password` field is required")

        with transaction.atomic():
            # Register user and set password
            instance = CustomUser(**data)
            instance.set_password(password)
            instance.save()

        self._user_verification_process(user=instance)
        return instance

    def update(self, instance: CustomUser, validated_data):
        data = validated_data.copy()

        # Purge extra data
        for key in ("password", "password_confirm"):
            if key in data:
                data.pop(key)

        # Set profile data
        for attribute, new_value in data.items():
            if not hasattr(instance, attribute):
                raise ValidationError("Invalid input data")

            if (new_value is not None) and (new_value != ""):
                if new_value != getattr(instance, attribute, None):
                    setattr(instance, attribute, new_value)

        instance.save()

        self._user_verification_process(user=instance)
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True, required=True, allow_null=False, allow_blank=False
    )
    new_password = serializers.CharField(
        write_only=True, required=True, allow_null=False, allow_blank=False
    )
    new_password_confirm = serializers.CharField(
        write_only=True, required=True, allow_null=False, allow_blank=False
    )

    def __init__(self, *args, **kwargs):
        try:
            self.user: CustomUser = kwargs.pop("user")
        except LookupError:
            raise LookupError("User is required")

        super().__init__(*args, **kwargs)

    def validate(self, data):
        data = super(ChangePasswordSerializer, self).validate(data)

        current_password = data.pop("current_password")
        if self.user.check_password(current_password) is False:
            raise AuthenticationFailed("Current password doesn't match the user")

        password = data["new_password"]
        try:
            password_confirm = data.pop("new_password_confirm")
            assert password == password_confirm
        except (AssertionError, LookupError):
            raise ValidationError("Passwords doesn't match")
        validate_password(password)

        return data

    def save(self, **kwargs):
        new_password = self.validated_data.pop("new_password")
        self.user.set_password(new_password)
        self.user.last_password_change = timezone.now()
        self.user.save()


class SendVerificationCodeSerializer(serializers.Serializer):
    identifier_field = serializers.ChoiceField(
        choices=[field.value for field in UserIdentifierField],
        write_only=True,
        allow_null=False,
        allow_blank=False,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        try:
            self.user: CustomUser = kwargs.pop("user")
        except LookupError:
            raise LookupError("User is required")

        super().__init__(*args, **kwargs)

    def validate(self, data):
        data = super(SendVerificationCodeSerializer, self).validate(data)
        identifier_field = data.pop("identifier_field")

        verification_kwargs = self.user.get_verification_kwargs(identifier_field=identifier_field)
        is_identifier_verified = getattr(self.user, f'is_{identifier_field}_verified', False)

        if is_identifier_verified is True or not verification_kwargs:
            raise ValidationError(f"User {identifier_field} is already verified")

        return {"verification_kwargs": verification_kwargs}

    def save(self, **kwargs):
        verification_kwargs = self.validated_data.pop("verification_kwargs")
        send_user_verification_code.apply_async(kwargs=verification_kwargs)


class OTPCodeVerifySerializer(serializers.Serializer):
    code = serializers.CharField(
        write_only=True,
        max_length=settings.VERIFICATION_CODE_DIGITS_COUNT,
        allow_null=False,
        allow_blank=False,
        required=True,
    )
    identifier_field = serializers.ChoiceField(
        choices=[field.value for field in UserIdentifierField],
        write_only=True,
        allow_null=False,
        allow_blank=False,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        try:
            self.user: CustomUser = kwargs.pop("user")
        except LookupError:
            raise LookupError("User is required")

        super().__init__(*args, **kwargs)

    def validate(self, data):
        data = super(OTPCodeVerifySerializer, self).validate(data)
        input_code = data.pop("code")
        identifier_field = data["identifier_field"]

        stored_code = get_user_verification_code(
            user_id=self.user.pk, identifier_field=identifier_field
        )
        if not stored_code:
            raise ValidationError("No code found for the user")

        if input_code != stored_code:
            raise ValidationError("Input code is not valid")

        return data

    def save(self, **kwargs):
        identifier_field = self.validated_data.pop("identifier_field")
        setattr(self.user, f"is_{identifier_field}_verified", True)
        self.user.save()
        delete_user_verification_code(
            user_id=self.user.id, identifier_field=identifier_field
        )
