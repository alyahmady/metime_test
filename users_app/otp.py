import random
from uuid import UUID

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from phonenumbers import PhoneNumber

from metime import celery_app
from metime.redis import get_redis_client
from metime.settings import UserIdentifierField
from users_app.models import CustomUser


def activation_key_generator() -> str:
    code_max_range = int("9" * settings.VERIFICATION_CODE_DIGITS_COUNT)
    code = str(random.randint(0, code_max_range))
    return code.rjust(settings.VERIFICATION_CODE_DIGITS_COUNT, "0")


def get_user_verification_code(user_id: str | int | UUID):
    code = cache.get(
        key=settings.VERIFICATION_CACHE_KEY.format(str(user_id)),
    )

    if isinstance(code, bytes):
        code = code.decode()
    if isinstance(code, int):
        code = str(code).rjust(settings.VERIFICATION_CODE_DIGITS_COUNT, "0")

    return code


def get_user_reset_password_code(user_id: str | int | UUID):
    code = cache.get(
        key=settings.RESET_PASSWORD_CACHE_KEY.format(str(user_id)),
    )

    if isinstance(code, bytes):
        code = code.decode()
    if isinstance(code, int):
        code = str(code).rjust(settings.VERIFICATION_CODE_DIGITS_COUNT, "0")

    return code


@celery_app.task(ignore_result=True)
def send_user_verification_code(
    is_verified: bool,
    user_id: str | int | UUID,
    user_identifier: str | PhoneNumber,
) -> None:
    if is_verified:
        raise ValueError("User is already verified")

    activation_key: str = activation_key_generator()
    message = f"""
        Your verification code is: {activation_key}
    """

    user_field, user_identifier = CustomUser.get_user_identifier_field(user_identifier)
    if user_field == UserIdentifierField.EMAIL:
        send_mail(
            subject=settings.VERIFICATION_EMAIL_SUBJECT,
            message=message,
            recipient_list=[user_identifier],
            from_email=None,
            fail_silently=True,
        )
    elif user_field == UserIdentifierField.PHONE:
        CustomUser.sms_user(phone=user_identifier.as_e164, message=message)

    redis_client = get_redis_client()
    redis_client.client().setex(
        name=cache.make_key(settings.VERIFICATION_CACHE_KEY.format(str(user_id))),
        value=activation_key,
        time=settings.VERIFICATION_TIMEOUT,
    )


@celery_app.task(ignore_result=True)
def send_user_reset_password_code(
    user_id: str | int | UUID,
    user_identifier: str | PhoneNumber,
):
    activation_key = activation_key_generator()

    message = f"""
        Your password recovery code is: {activation_key}
    """

    user_field, user_identifier = CustomUser.get_user_identifier_field(user_identifier)
    if user_field == UserIdentifierField.EMAIL:
        send_mail(
            subject=settings.RESET_PASSWORD_EMAIL_SUBJECT,
            message=message,
            recipient_list=[user_identifier],
            from_email=None,
            fail_silently=True,
        )
    elif user_field == UserIdentifierField.PHONE:
        CustomUser.sms_user(phone=user_identifier.as_e164, message=message)

    redis_client = get_redis_client()
    redis_client.setex(
        name=cache.make_key(settings.RESET_PASSWORD_CACHE_KEY.format(str(user_id))),
        value=activation_key,
        time=settings.RESET_PASSWORD_TIMEOUT,
    )
