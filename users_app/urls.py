from django.urls import path

from users_app.views import UserViewSet

urlpatterns = [
    path("", UserViewSet.as_view({"post": "create"}), name="user-register"),
]
