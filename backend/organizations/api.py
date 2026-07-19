

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsOrganizationMember
from core.tenant import (
    MANAGER_ROLES,
    has_organization_role,
    organization_ids_for,
)

from .models import Organization, OrganizationMembership
from .serializers import MembershipSerializer, OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Manage organizations visible to the authenticated user.

    Organization list and detail access are tenant-scoped.
    Organization creation automatically creates an owner membership.
    Only an owner may delete an organization.
    """

    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        organization_ids = organization_ids_for(self.request.user)

        queryset = Organization.objects.all().order_by("id")

        if organization_ids is None:
            return queryset

        return queryset.filter(id__in=organization_ids)

    @transaction.atomic
    def perform_create(self, serializer):
        organization = serializer.save()

        OrganizationMembership.objects.create(
            organization=organization,
            user=self.request.user,
            role=OrganizationMembership.Role.OWNER,
            is_active=True,
        )

    def perform_destroy(self, instance):
        """
        Only an organization owner or superuser may delete an organization.
        """
        if not has_organization_role(
            self.request.user,
            instance,
            {OrganizationMembership.Role.OWNER},
        ):
            raise PermissionDenied(
                "Only an organization owner may delete this organization."
            )

        instance.delete()


class MembershipViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Manage organization memberships.

    Security rules:
    - Only organization managers may access membership endpoints.
    - Organization membership records are tenant-scoped.
    - Memberships cannot be moved between organizations.
    - Existing membership users cannot be replaced.
    - Only owners may create or modify manager-level memberships.
    - Every organization must retain at least one active owner.
    """

    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            OrganizationMembership.objects
            .select_related("user", "organization")
            .order_by("organization_id", "id")
        )

        organization_id = self.kwargs.get("organization_pk")

        if organization_id is None:
            return queryset.none()

        queryset = queryset.filter(
            organization_id=organization_id,
        )

        user = self.request.user

        if user.is_superuser:
            return queryset

        return queryset.filter(
            organization__is_active=True,
            organization__memberships__user=user,
            organization__memberships__is_active=True,
            organization__memberships__role__in=MANAGER_ROLES,
        ).distinct()

    def _managed_organization(self) -> Organization:
        """
        Return the requested organization only when the user manages it.

        Returning 404 for both missing and unauthorized organizations reduces
        organization-ID enumeration.
        """
        organization_id = self.kwargs.get("organization_pk")

        if organization_id is None:
            raise ValidationError(
                {"organization": "An organization identifier is required."}
            )

        queryset = Organization.objects.filter(is_active=True)

        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                memberships__user=self.request.user,
                memberships__is_active=True,
                memberships__role__in=MANAGER_ROLES,
            ).distinct()

        return get_object_or_404(queryset, pk=organization_id)

    def _requester_is_owner(self, organization: Organization) -> bool:
        return has_organization_role(
            self.request.user,
            organization,
            {OrganizationMembership.Role.OWNER},
        )

    def _validate_manager_role_change(
        self,
        organization: Organization,
        current_role: str | None,
        requested_role: str | None,
    ) -> None:
        """
        Prevent administrators from creating, promoting, demoting, or
        disabling owner/administrator memberships.
        """
        touches_manager_role = (
            current_role in MANAGER_ROLES
            or requested_role in MANAGER_ROLES
        )

        if touches_manager_role and not self._requester_is_owner(organization):
            raise PermissionDenied(
                "Only an organization owner may manage owner or "
                "administrator memberships."
            )

    @staticmethod
    def _active_owner_count(organization: Organization) -> int:
        return organization.memberships.filter(
            role=OrganizationMembership.Role.OWNER,
            is_active=True,
        ).count()

    @transaction.atomic
    def perform_create(self, serializer):
        organization = self._managed_organization()
        requested_role = serializer.validated_data.get("role")

        self._validate_manager_role_change(
            organization=organization,
            current_role=None,
            requested_role=requested_role,
        )

        serializer.save(organization=organization)

    @transaction.atomic
    def perform_update(self, serializer):
        organization = self._managed_organization()

        instance = OrganizationMembership.objects.select_for_update().get(
            pk=serializer.instance.pk
        )
        serializer.instance = instance

        if instance.organization_id != organization.id:
            raise PermissionDenied("Membership does not belong to this organization.")

        requested_organization = serializer.validated_data.get("organization")

        if (
            requested_organization is not None
            and requested_organization.pk != instance.organization_id
        ):
            raise ValidationError(
                {"organization": "A membership cannot be moved to another organization."}
            )

        requested_user = serializer.validated_data.get("user")

        if requested_user is not None and requested_user.pk != instance.user_id:
            raise ValidationError(
                {"user": "The user assigned to a membership cannot be changed."}
            )

        requested_role = serializer.validated_data.get(
            "role",
            instance.role,
        )
        requested_is_active = serializer.validated_data.get(
            "is_active",
            instance.is_active,
        )

        self._validate_manager_role_change(
            organization=organization,
            current_role=instance.role,
            requested_role=requested_role,
        )

        removes_active_owner = (
            instance.role == OrganizationMembership.Role.OWNER
            and instance.is_active
            and (
                requested_role != OrganizationMembership.Role.OWNER
                or requested_is_active is False
            )
        )

        if removes_active_owner:
            # Evaluate locked owner records to prevent concurrent requests from
            # removing the final active owner at the same time.
            list(
                organization.memberships.select_for_update().filter(
                    role=OrganizationMembership.Role.OWNER,
                    is_active=True,
                )
            )

            if self._active_owner_count(organization) <= 1:
                raise ValidationError(
                    {
                        "role": (
                            "An organization must retain at least one active owner."
                        )
                    }
                )

        serializer.save(
            organization=organization,
            user=instance.user,
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        organization = self._managed_organization()

        locked_instance = OrganizationMembership.objects.select_for_update().get(
            pk=instance.pk
        )

        if locked_instance.organization_id != organization.id:
            raise PermissionDenied("Membership does not belong to this organization.")

        self._validate_manager_role_change(
            organization=organization,
            current_role=locked_instance.role,
            requested_role=None,
        )

        if (
            locked_instance.role == OrganizationMembership.Role.OWNER
            and locked_instance.is_active
        ):
            list(
                organization.memberships.select_for_update().filter(
                    role=OrganizationMembership.Role.OWNER,
                    is_active=True,
                )
            )

            if self._active_owner_count(organization) <= 1:
                raise ValidationError(
                    {
                        "detail": (
                            "An organization must retain at least one active owner."
                        )
                    }
                )

        locked_instance.delete()