from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from metime.settings import UserIdentifierField
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
            "is_email_verified",
            "is_phone_verified",
        )
        read_only_fields = (
            "id",
            "date_joined",
            "is_active",
            "is_email_verified",
            "is_phone_verified",
        )
        extra_kwargs = {
            "email": {"required": False, "allow_null": False},
        }

    def _user_verification_process(self, user: CustomUser):
        # Send verification code
        if not user.is_verified:
            verification_kwargs = {"user": user}
            if user.email:
                verification_kwargs["user_field"] = UserIdentifierField.EMAIL
            elif user.phone:
                verification_kwargs["user_field"] = UserIdentifierField.PHONE

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
        for key in ("password", "password_confirm"):
            if key not in data:
                raise ValidationError(f"`{key}` field is required")

        if "email" not in data and "phone" not in data:
            raise ValidationError(
                "Either `phone` or `email` fields must be in the request payload"
            )

        password = data.pop("password")
        with transaction.atomic():
            # Register user and set password
            instance = CustomUser(**data)
            instance.set_password(password)
            instance.save()

        self._user_verification_process(user=instance)
        return instance
