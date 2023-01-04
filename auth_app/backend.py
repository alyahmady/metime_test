import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    AuthenticationFailed,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.utils import datetime_from_epoch


class AuthHelper:
    def is_user_active(self, user: get_user_model()) -> bool:
        is_active = getattr(user, "is_active", False)
        return is_active

    def user_can_authenticate(self, user: get_user_model()) -> bool:
        can_login = getattr(user, "can_login", False)
        return self.is_user_active(user) and can_login


class CustomUserAuthBackend(AuthHelper, ModelBackend):
    UserModel = get_user_model()

    def authenticate(self, request, phone=None, email=None, password=None):
        if not phone and not email:
            return None

        try:
            user = self.UserModel._default_manager.get(phone=phone, email=email)
        except self.UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.is_user_active(user):
            return user

        return None


class CustomJWTAuthentication(AuthHelper, JWTAuthentication):
    www_authenticate_realm = "api"
    media_type = "application/json"

    def validate_token_iat(self, validated_token: Token, user: get_user_model()):
        """
        Validate `iat` claim, beside other validations, to make sure that `iat`
         is not before user's last password change date.

        :param validated_token: `Token` class instance of the raw JWT
        :raise InvalidToken
        """

        iat_value = validated_token.payload["iat"]
        iat_time: datetime.datetime = datetime_from_epoch(iat_value)

        if isinstance(user.last_password_change, datetime.datetime):
            if iat_time <= user.last_password_change:
                raise InvalidToken(_("Token is expired. User must re-login"))

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            user: get_user_model() = self.user_model._default_manager.get(
                **{api_settings.USER_ID_FIELD: user_id}
            )
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not self.user_can_authenticate(user):
            raise AuthenticationFailed(_("User is not verified"), code="user_inactive")

        self.validate_token_iat(validated_token, user)

        return user
