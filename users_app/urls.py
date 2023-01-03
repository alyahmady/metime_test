from django.urls import path

from users_app.views import UserViewSet

urlpatterns = [
    path("", UserViewSet.as_view({"post": "create"}), name="user-register"),
    path("<int:user_id>", UserViewSet.as_view({"patch": "update"}), name="user-update"),
]
