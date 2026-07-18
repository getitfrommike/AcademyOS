from django.contrib import admin
from core.admin import TenantRestrictedAdminMixin
from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(TenantRestrictedAdminMixin, admin.ModelAdmin):
    list_display = ("created_at", "organization", "actor", "action", "resource_type", "resource_id")
    list_filter = ("action", "organization", "created_at")
    search_fields = ("description", "resource_type", "resource_id", "actor__email")
    readonly_fields = [field.name for field in AuditEvent._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
