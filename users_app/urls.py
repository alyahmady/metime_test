from django.urls import path

from users_app.views import UserViewSet, VerificationViewSet

urlpatterns = [
    path("", UserViewSet.as_view({"post": "create"}), name="user-register"),
    path("<int:user_id>", UserViewSet.as_view({"patch": "update"}), name="user-update"),
    path(
        "<int:user_id>/password",
        UserViewSet.as_view({"put": "change_password"}),
        name="user-password-change",
    ),
    path(
        "verification",
        VerificationViewSet.as_view({"post": "otp_code_verify"}),
        name="otp-code-verify",
    ),
    path(
        "verification/resend",
        VerificationViewSet.as_view({"put": "resend_verification_code"}),
        name="resend-verification-code",
    ),
]
