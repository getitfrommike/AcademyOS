from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.tenant import MANAGER_ROLES, REVIEW_ROLES, has_organization_role


class IsOrganizationMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        organization = getattr(obj, "organization", obj if obj.__class__.__name__ == "Organization" else None)
        if organization is None:
            return False
        roles = REVIEW_ROLES if request.method in SAFE_METHODS else MANAGER_ROLES
        return has_organization_role(request.user, organization, roles)
