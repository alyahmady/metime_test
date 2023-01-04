from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from metime.permissions import Forbidden, IsOwnerUser, IsActiveUser
from users_app.models import CustomUser
from users_app.serializers import (
    UserSerializer,
    ChangePasswordSerializer,
    OTPCodeVerifySerializer,
    ResendVerificationCodeSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.filter(is_active=True)
    lookup_field = "id"
    lookup_url_kwarg = "user_id"
    throttle_scope = None

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "user_register"
        elif self.action == "update":
            self.throttle_scope = "user_update"
        elif self.action == "change_password":
            self.throttle_scope = "change_password"
        return super(UserViewSet, self).get_throttles()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        elif self.action in ["update", "change_password"]:
            return [IsOwnerUser()]
        return [Forbidden()]

    def perform_create(self, serializer):
        with transaction.atomic():
            return serializer.save()

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save()

    @action(detail=True, methods=["put"], permission_classes=[IsOwnerUser])
    def change_password(self, request, *args, **kwargs):
        data = request.data.copy()

        serializer = ChangePasswordSerializer(user=request.user, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            serializer.save()

        return Response(status=status.HTTP_200_OK)


class VerificationViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.filter(is_active=True)
    lookup_field = "id"
    lookup_url_kwarg = "user_id"
    throttle_scope = None

    def get_throttles(self):
        if self.action == "resend_verification_code":
            self.throttle_scope = "resend_verification_code"
        elif self.action == "otp_code_verify":
            self.throttle_scope = "otp_code_verify"
        return super(VerificationViewSet, self).get_throttles()

    def get_permissions(self):
        if self.action in ["otp_code_verify", "resend_verification_code"]:
            return [IsActiveUser()]
        return [Forbidden()]

    @action(detail=True, methods=["post"], permission_classes=[IsActiveUser])
    def resend_verification_code(self, request, *args, **kwargs):
        data = request.data.copy()

        serializer = ResendVerificationCodeSerializer(user=request.user, data=data)
        serializer.is_valid(raise_exception=True)
        user_identifier = serializer.save()

        # TODO: email/phone must be hidden with * in response
        return Response(
            data={"message": f"Verification code is sent to {user_identifier}"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsActiveUser])
    def otp_code_verify(self, request, *args, **kwargs):
        data = request.data.copy()

        serializer = OTPCodeVerifySerializer(user=request.user, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            serializer.save()

        return Response(
            data={"message": "Account activated"}, status=status.HTTP_200_OK
        )
