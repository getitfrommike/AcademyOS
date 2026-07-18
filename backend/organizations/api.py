from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied

from core.permissions import IsOrganizationMember
from core.tenant import MANAGER_ROLES, organization_ids_for
from .models import Organization, OrganizationMembership
from .serializers import MembershipSerializer, OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        ids = organization_ids_for(self.request.user)
        queryset = Organization.objects.all()
        return queryset if ids is None else queryset.filter(id__in=ids)

    def perform_create(self, serializer):
        organization = serializer.save()
        OrganizationMembership.objects.create(
            organization=organization,
            user=self.request.user,
            role=OrganizationMembership.Role.OWNER,
        )


class MembershipViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = MembershipSerializer

    def get_queryset(self):
        ids = organization_ids_for(self.request.user)
        queryset = OrganizationMembership.objects.select_related("user", "organization")
        return queryset if ids is None else queryset.filter(organization_id__in=ids)

    def _organization(self):
        organization_id = self.kwargs["organization_pk"]
        try:
            organization = Organization.objects.get(pk=organization_id)
        except Organization.DoesNotExist as exc:
            raise PermissionDenied("Organization not available.") from exc
        if not self.request.user.is_superuser and not organization.memberships.filter(
            user=self.request.user, is_active=True, role__in=MANAGER_ROLES
        ).exists():
            raise PermissionDenied("Manager access is required.")
        return organization

    def perform_create(self, serializer):
        serializer.save(organization=self._organization())

    def perform_update(self, serializer):
        self._organization()
        serializer.save()

    def perform_destroy(self, instance):
        organization = self._organization()
        if instance.role == OrganizationMembership.Role.OWNER and organization.memberships.filter(
            role=OrganizationMembership.Role.OWNER, is_active=True
        ).count() <= 1:
            raise PermissionDenied("An organization must retain at least one active owner.")
        instance.delete()
