from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from users_app.models import CustomUser
from users_app.otp import send_user_verification_code


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
        # Send verification code
        if not user.is_verified:
            verification_kwargs = {"user_id": user.pk}

            # IMPORTANT -> At first attempt (registration), verification code
            #  will be sent by email, if both phone and email are passed

            if user.email and user.is_email_verified is False:
                verification_kwargs["user_identifier"] = user.email
                verification_kwargs["is_identifier_verified"] = user.is_email_verified
            elif user.phone and user.is_phone_verified is False:
                verification_kwargs["user_identifier"] = user.phone.as_e164
                verification_kwargs["is_identifier_verified"] = user.is_phone_verified
            else:
                return

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

        current_password = data["current_password"]
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
        self.user.save()
