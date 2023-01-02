import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from metime import celery_app


def activation_key_generator() -> str:
    code_max_range = int("9" * settings.VERIFICATION_CODE_DIGITS_COUNT)
    code = str(random.randint(0, code_max_range))
    return code.rjust(settings.VERIFICATION_CODE_DIGITS_COUNT, "0")


@celery_app.task(ignore_result=True)
def send_user_verification_code(
    user: get_user_model(), user_field: settings.UserIdentifierField
) -> None:
    if user.is_verified:
        raise ValueError("User is already verified")

    activation_key: str = activation_key_generator()
    message = f"""
        Your verification code is: {activation_key}
    """

    if user_field == settings.UserIdentifierField.EMAIL:
        user.email_user(
            subject=settings.VERIFICATION_EMAIL_SUBJECT,
            message=message,
            fail_silently=True,
        )
    elif user_field == settings.UserIdentifierField.PHONE:
        user.sms_user(message=message)

    cache.set(
        key=settings.VERIFICATION_CACHE_KEY.format(str(user.id)),
        value=activation_key,
        timeout=settings.VERIFICATION_TIMEOUT,
    )


@celery_app.task(ignore_result=True)
def send_user_reset_password_code(
    user: get_user_model(), user_field: settings.UserIdentifierField
):
    activation_key = activation_key_generator()

    message = f"""
        Your password recovery code is: {activation_key}
    """

    if user_field == settings.UserIdentifierField.EMAIL:
        user.email_user(
            subject=settings.FORGOT_PASSWORD_EMAIL_SUBJECT,
            message=message,
            fail_silently=True,
        )
    elif user_field == settings.UserIdentifierField.PHONE:
        user.sms_user(message=message)

    cache.set(
        key=settings.FORGOT_PASSWORD_CACHE_KEY.format(str(user.id)),
        value=activation_key,
        timeout=settings.FORGOT_PASSWORD_TIMEOUT,
    )
