from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AcademyOSUserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (
        (
            "AcademyOS Profile",
            {
                "fields": (
                    "display_name",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "AcademyOS Profile",
            {
                "fields": (
                    "email",
                    "display_name",
                )
            },
        ),
    )

    list_display = (
        "email",
        "username",
        "display_name",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "email",
        "username",
        "display_name",
    )

    ordering = ("email",)
