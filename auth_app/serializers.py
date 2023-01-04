from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import PasswordField
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainSerializer(serializers.Serializer):
    email_field = get_user_model().EMAIL_FIELD
    phone_field = get_user_model().PHONE_FIELD
    token_class = None

    default_error_messages = {
        "no_active_account": _("No account found with the given credentials")
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

        self.fields[self.email_field] = serializers.EmailField(
            allow_null=True, allow_blank=False, required=False
        )
        self.fields[self.phone_field] = PhoneNumberField(
            allow_null=True, allow_blank=False, required=False
        )
        self.fields["password"] = PasswordField()

    def validate(self, attrs: dict):
        authenticate_kwargs = {
            "password": attrs["password"],
            self.email_field: attrs.get(self.email_field),
            self.phone_field: attrs.get(self.phone_field),
        }

        if (
            not authenticate_kwargs[self.email_field]
            and not authenticate_kwargs[self.phone_field]
        ):
            raise ValidationError("Either phone or email field must be filled")

        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        return {}

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)


class CustomTokenObtainPairSerializer(CustomTokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        # Add custom data here
        now = timezone.now()
        refresh.access_token.set_iat(at_time=now)
        refresh.access_token.set_exp(from_time=now)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data
