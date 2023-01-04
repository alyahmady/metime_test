from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_scope = "token_obtain"
    permission_classes = [permissions.AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    throttle_scope = "token_refresh"
    permission_classes = [permissions.AllowAny]
