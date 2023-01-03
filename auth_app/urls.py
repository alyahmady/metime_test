from django.urls import path

from auth_app.views import CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]