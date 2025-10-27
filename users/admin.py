from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ("updated_at",)
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active", "is_verified")
    list_filter = ("is_staff", "is_active", "is_verified", "gender")

    # admin
    fieldsets = (
        ("Login Info", {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "bio", "profile_image", "phone_number", "gender", "date_of_birth")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined", "updated_at")}),
        ("Verification", {"fields": ("is_verified",)}),
        ("Role Info", {"fields": ("role",)}),        

    )

    # create new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
