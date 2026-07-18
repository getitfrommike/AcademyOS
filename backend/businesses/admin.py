from django.contrib import admin

from core.admin import TenantRestrictedAdminMixin
from .models import EducationBusiness


@admin.register(EducationBusiness)
class EducationBusinessAdmin(TenantRestrictedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "organization", "business_type", "is_active", "updated_at")
    list_filter = ("business_type", "is_active", "organization")
    search_fields = ("name", "slug", "organization__name")
    autocomplete_fields = ("organization", "created_by", "updated_by")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("id", "created_at", "updated_at")
