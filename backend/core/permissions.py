from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from organizations.models import Organization

from core.tenant import (
    MANAGER_ROLES,
    REVIEW_ROLES,
    has_organization_role,
)


class IsOrganizationMember(BasePermission):
    """
    Enforce organization-level object authorization.

    Access rules:
    - Unauthenticated or inactive users are denied.
    - Superusers are permitted through has_organization_role().
    - Safe requests require a review-level organization role.
    - Write requests require an owner or administrator role.
    - Objects without an identifiable organization are denied.

    This permission protects individual objects. API querysets must still be
    filtered by organization to prevent cross-tenant exposure in list views.
    """

    message = "You do not have permission to access this organization resource."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Require an authenticated, active account before processing the request.

        Create and list authorization must also be enforced by the API view
        because those requests may not have an object available yet.
        """
        user = request.user

        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and getattr(user, "is_active", False)
        )

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        """
        Check the user's role for the organization associated with the object.
        """
        organization = self._get_organization(obj)

        if organization is None:
            return False

        required_roles = (
            REVIEW_ROLES
            if request.method in SAFE_METHODS
            else MANAGER_ROLES
        )

        return has_organization_role(
            user=request.user,
            organization=organization,
            roles=required_roles,
        )

    @staticmethod
    def _get_organization(obj: Any) -> Organization | None:
        """
        Resolve an Organization from either an Organization instance or an
        object containing a direct `organization` relationship.

        Deny access when the object has no valid organization relationship.
        """
        if isinstance(obj, Organization):
            return obj

        organization = getattr(obj, "organization", None)

        if isinstance(organization, Organization):
            return organization

        return None