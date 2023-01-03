from rest_framework.permissions import BasePermission


class Forbidden(BasePermission):
    message = "You do not have permission to perform this action"

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False
