from django.contrib import admin

from core.admin import TenantRestrictedAdminMixin

from .models import Program


@admin.register(Program)
class ProgramAdmin(TenantRestrictedAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "academy",
        "organization",
        "status",
        "is_featured",
        "created_at",
    )

    list_filter = (
        "status",
        "is_featured",
        "organization",
        "academy",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "academy__name",
        "organization__name",
    )

    autocomplete_fields = (
        "organization",
        "academy",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )