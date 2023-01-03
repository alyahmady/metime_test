from django.db import transaction
from rest_framework import viewsets, permissions

from users_app.models import CustomUser
from users_app.permissions import Forbidden
from users_app.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.filter(is_active=True)
    lookup_field = "id"
    lookup_url_kwarg = "user_id"
    throttle_scope = None

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "user_register"
        return super(UserViewSet, self).get_throttles()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [Forbidden()]

    def perform_create(self, serializer, **kwargs):
        with transaction.atomic():
            return serializer.save(**kwargs)
