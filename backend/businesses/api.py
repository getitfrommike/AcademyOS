from typing import Any

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response

from core.permissions import IsOrganizationMember
from core.tenant import MANAGER_ROLES, organization_ids_for
from organizations.models import Organization

from .models import EducationBusiness
from .serializers import EducationBusinessSerializer


class EducationBusinessViewSet(viewsets.ModelViewSet):
    """
    Manage education businesses with tenant isolation.

    Read access is limited to businesses belonging to organizations where
    the requesting user has an active membership.

    Create, update, and delete operations require an active manager role,
    unless the requesting user is a superuser.
    """

    serializer_class = EducationBusinessSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        """
        Return only businesses visible to the authenticated user.

        Superusers receive all businesses because organization_ids_for()
        returns None for unrestricted access.
        """
        organization_ids = organization_ids_for(self.request.user)

        queryset = (
            EducationBusiness.objects
            .select_related(
                "organization",
                "created_by",
                "updated_by",
            )
            .order_by("name")
        )

        if organization_ids is None:
            return queryset

        return queryset.filter(
            organization_id__in=organization_ids,
            organization__is_active=True,
        )

    @transaction.atomic
    def perform_create(
        self,
        serializer: EducationBusinessSerializer,
    ) -> None:
        """
        Create a business inside an authorized organization.
        """
        organization = self._get_requested_organization()

        self._require_manager_access(organization)

        serializer.save(
            organization=organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    @transaction.atomic
    def perform_update(
        self,
        serializer: EducationBusinessSerializer,
    ) -> None:
        """
        Require manager access before changing a business.
        """
        business = self.get_object()

        self._require_manager_access(
            business.organization,
        )

        serializer.save(
            updated_by=self.request.user,
        )

    @transaction.atomic
    def destroy(
        self,
        request: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Require manager access before deleting a business.
        """
        business = self.get_object()

        self._require_manager_access(
            business.organization,
        )

        self.perform_destroy(business)

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    def _get_requested_organization(
        self,
    ) -> Organization:
        """
        Resolve and validate the organization supplied during creation.
        """
        organization_id = self.request.data.get(
            "organization_id"
        )

        if not organization_id:
            raise ValidationError(
                {
                    "organization_id": (
                        "An organization ID is required."
                    )
                }
            )

        try:
            organization = Organization.objects.get(
                pk=organization_id,
            )
        except (
            Organization.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise ValidationError(
                {
                    "organization_id": (
                        "A valid organization ID is required."
                    )
                }
            ) from exc

        if not organization.is_active:
            raise ValidationError(
                {
                    "organization_id": (
                        "Businesses cannot be created in an "
                        "inactive organization."
                    )
                }
            )

        return organization

    def _require_manager_access(
        self,
        organization: Organization,
    ) -> None:
        """
        Require an active owner or administrator membership.

        Superusers bypass organization membership checks.
        """
        user = self.request.user

        if user.is_superuser:
            return

        has_manager_access = (
            organization.memberships.filter(
                user=user,
                is_active=True,
                role__in=MANAGER_ROLES,
            ).exists()
        )

        if not has_manager_access:
            raise PermissionDenied(
                "Owner or administrator access is required."
            )