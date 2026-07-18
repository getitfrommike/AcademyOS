from django.contrib import admin
from django.core.exceptions import PermissionDenied

from core.tenant import MANAGER_ROLES, organization_ids_for


class TenantRestrictedAdminMixin:
    """Restrict non-superuser admin access to organizations they belong to."""

    organization_lookup = "organization_id"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        ids = organization_ids_for(request.user)
        if ids is None:
            return queryset
        return queryset.filter(**{f"{self.organization_lookup}__in": ids})

    def has_view_permission(self, request, obj=None):
        allowed = super().has_view_permission(request, obj)
        return allowed and self._object_allowed(request, obj)

    def has_change_permission(self, request, obj=None):
        allowed = super().has_change_permission(request, obj)
        return allowed and self._object_allowed(request, obj, require_manager=True)

    def has_delete_permission(self, request, obj=None):
        allowed = super().has_delete_permission(request, obj)
        return allowed and self._object_allowed(request, obj, require_manager=True)

    def _object_allowed(self, request, obj, require_manager=False):
        if obj is None or request.user.is_superuser:
            return True
        organization = self.get_object_organization(obj)
        if organization is None:
            return False
        memberships = request.user.organization_memberships.filter(
            organization=organization,
            is_active=True,
        )
        if require_manager:
            memberships = memberships.filter(role__in=MANAGER_ROLES)
        return memberships.exists()

    def get_object_organization(self, obj):
        return getattr(obj, "organization", None)

    def save_model(self, request, obj, form, change):
        if hasattr(obj, "created_by_id") and not obj.created_by_id:
            obj.created_by = request.user
        if hasattr(obj, "updated_by_id"):
            obj.updated_by = request.user
        if not self._object_allowed(request, obj, require_manager=True):
            raise PermissionDenied("You cannot modify another organization's data.")
        super().save_model(request, obj, form, change)
