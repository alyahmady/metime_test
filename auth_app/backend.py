from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class CustomUserAuthBackend(ModelBackend):
    UserModel = get_user_model()

    def authenticate(self, request, phone=None, email=None, password=None):
        if not phone and not email:
            return None

        try:
            user = self.UserModel._default_manager.get(phone=phone, email=email)
        except self.UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False or is_verified=False.
        """
        is_active = getattr(user, "is_active", False)
        is_email_verified = getattr(user, "is_email_verified", False)
        return is_active and is_email_verified
