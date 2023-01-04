from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from metime.permissions import Forbidden, IsOwnerUser
from users_app.models import CustomUser
from users_app.serializers import UserSerializer, ChangePasswordSerializer


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

    @action(methods=["get"], permission_classes=[IsOwnerUser])
    def change_password(self, request, *args, **kwargs):
        data = request.data.copy()

        serializer = ChangePasswordSerializer(user=request.user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)
