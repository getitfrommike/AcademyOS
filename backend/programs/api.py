from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers, viewsets
from rest_framework.exceptions import PermissionDenied

from core.permissions import IsOrganizationMember
from core.tenant import MANAGER_ROLES, organization_ids_for
from organizations.models import Organization

from .models import Program
from .serializers import ProgramSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        organization_ids = organization_ids_for(
            self.request.user
        )

        queryset = Program.objects.select_related(
            "organization",
            "academy",
            "created_by",
            "updated_by",
        )

        if organization_ids is None:
            return queryset

        return queryset.filter(
            organization_id__in=organization_ids
        )

    def _get_requested_organization(self):
        organization_id = self.request.data.get(
            "organization_id"
        )

        if not organization_id:
            raise serializers.ValidationError(
                {
                    "organization_id": (
                        "An organization is required."
                    )
                }
            )

        try:
            organization = Organization.objects.get(
                id=organization_id,
            )
        except (
            Organization.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise serializers.ValidationError(
                {
                    "organization_id": (
                        "A valid organization is required."
                    )
                }
            ) from exc

        if not organization.is_active:
            raise serializers.ValidationError(
                {
                    "organization_id": (
                        "The selected organization is inactive."
                    )
                }
            )

        return organization

    def _require_manager_access(self, organization):
        if self.request.user.is_superuser:
            return

        has_manager_access = (
            organization.memberships.filter(
                user=self.request.user,
                is_active=True,
                role__in=MANAGER_ROLES,
            ).exists()
        )

        if not has_manager_access:
            raise PermissionDenied(
                "Manager access is required."
            )

    def perform_create(self, serializer):
        organization = self._get_requested_organization()
        self._require_manager_access(organization)

        academy_id = self.request.data.get("academy_id")

        academy = serializer.validate_academy_for_organization(
            academy_id,
            organization,
        )

        serializer.save(
            organization=organization,
            academy=academy,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        program = self.get_object()

        self._require_manager_access(
            program.organization
        )

        serializer.save(
            updated_by=self.request.user,
        )

    def perform_destroy(self, instance):
        self._require_manager_access(
            instance.organization
        )

        instance.delete()