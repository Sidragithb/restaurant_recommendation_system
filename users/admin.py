# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin config for your CustomUser."""

    # list view columns
    list_display  = ("id", "username", "email", "phone_number", "is_staff", "is_verified")
    list_filter   = ("is_staff", "is_superuser", "is_verified", "is_active")

    # which fields are read‑only
    readonly_fields = ("last_login", "date_joined")

    # field groups on detail page
    fieldsets = (
        (None,               {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "phone_number")}),
        (_("Verification"),  {"fields": ("is_verified", "otp")}),
        (_("Permissions"),   {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # fields shown when creating a new user in admin
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "phone_number", "password1", "password2"),
        }),
    )

    ordering = ("id",)
