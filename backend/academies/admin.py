from django.contrib import admin

from core.admin import TenantRestrictedAdminMixin

from .models import Academy


@admin.register(Academy)
class AcademyAdmin(TenantRestrictedAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "organization",
        "slug",
        "is_public",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_public",
        "is_active",
        "organization",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "organization__name",
        "custom_domain",
    )

    autocomplete_fields = (
        "organization",
        "business",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )