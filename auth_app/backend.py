from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings


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

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            user = self.user_model._default_manager.get(
                **{api_settings.USER_ID_FIELD: user_id}
            )
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not self.user_can_authenticate(user):
            raise AuthenticationFailed(_("User is not verified"), code="user_inactive")

        return user
