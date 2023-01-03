from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_scope = "token_obtain"


class CustomTokenRefreshView(TokenRefreshView):
    throttle_scope = "token_refresh"
