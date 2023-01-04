from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission, IsAuthenticated


class Forbidden(BasePermission):
    message = "You do not have permission to perform this action"

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class IsActiveUser(IsAuthenticated):
    message = "User is deactivated"

    def has_permission(self, request, view):
        is_authenticated = super(IsActiveUser, self).has_permission(request, view)

        conditions = (
            is_authenticated,
            request.user.is_active is True,
            (not isinstance(request.user, AnonymousUser)),
            (isinstance(request.user, get_user_model())),
        )
        return all(conditions)


class IsVerifiedActiveUser(IsActiveUser):
    message = "User is not verified"

    def has_permission(self, request, view):
        is_active_user = super(IsVerifiedActiveUser, self).has_permission(request, view)

        return is_active_user and getattr(request.user, "can_login", False) is True


class IsOwnerUser(IsVerifiedActiveUser):
    message = "Oops! You do not have permission to perform this action"

    def has_object_permission(self, request, view, obj):
        conditions = [
            (isinstance(obj, get_user_model()) and obj.pk == request.user.pk),
            getattr(obj, "user_id", None) == request.user.pk,
            getattr(getattr(obj, "user", None), "id", None) == request.user.pk,
        ]
        return any(conditions)


class IsAdminUser(IsVerifiedActiveUser):
    message = "You do not have permission to perform this action"

    def has_permission(self, request, view):
        is_verified_active_user = super(IsActiveUser, self).has_permission(
            request, view
        )

        return is_verified_active_user and (
            request.user.is_staff or request.user.is_superuser
        )
