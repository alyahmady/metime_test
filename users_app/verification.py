import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache


def activation_key_generator() -> str:
    code_max_range = int("9" * settings.VERIFICATION_CODE_DIGITS_COUNT)
    code = str(random.randint(0, code_max_range))
    return code.rjust(settings.VERIFICATION_CODE_DIGITS_COUNT, "0")


def send_user_verification_code(user: get_user_model()) -> None:
    if user.is_verified:
        raise ValueError("User is already verified")

    activation_key: str = activation_key_generator()
    email_message = f"""
        Your verification code is: {activation_key}
    """
    user.email_user(
        settings.VERIFICATION_EMAIL_SUBJECT, email_message, fail_silently=True
    )

    cache.set(
        key=settings.VERIFICATION_CACHE_KEY.format(str(user.id)),
        value=activation_key,
        timeout=settings.VERIFICATION_TIMEOUT,
    )


def send_user_reset_password_code(user: get_user_model()):
    activation_key = activation_key_generator()

    email_message = f"""
        Your password recovery code is: {activation_key}
    """
    user.email_user(
        settings.FORGOT_PASSWORD_EMAIL_SUBJECT, email_message, fail_silently=True
    )

    cache.set(
        key=settings.FORGOT_PASSWORD_CACHE_KEY.format(str(user.id)),
        value=activation_key,
        timeout=settings.FORGOT_PASSWORD_TIMEOUT,
    )
