from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users_app.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "phone",
        "full_name",
        "is_active",
        "is_verified",
        "date_joined",
        "last_login",
    )
    list_display_links = ("email", "phone", "full_name")
    list_filter = ("is_superuser", "is_active", "is_verified")
    fieldsets = (
        (None, {"fields": ("email", "phone", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_verified")}),
        ("Information", {"fields": ("first_name", "last_name")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "phone", "password1", "password2")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_verified")}),
        ("Information", {"fields": ("first_name", "last_name")}),
    )
    search_fields = ("email", "phone", "first_name", "last_name")
    ordering = ("-date_joined", "last_name")
    empty_value_display = "---"
