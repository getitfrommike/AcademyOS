from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from core.permissions import IsOrganizationMember
from core.tenant import MANAGER_ROLES, organization_ids_for
from organizations.models import Organization
from .models import EducationBusiness
from .serializers import EducationBusinessSerializer


class EducationBusinessViewSet(viewsets.ModelViewSet):
    serializer_class = EducationBusinessSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        ids = organization_ids_for(self.request.user)
        queryset = EducationBusiness.objects.select_related("organization")
        return queryset if ids is None else queryset.filter(organization_id__in=ids)

    def perform_create(self, serializer):
        organization_id = self.request.data.get("organization_id")
        try:
            organization = Organization.objects.get(pk=organization_id)
        except (Organization.DoesNotExist, ValueError, TypeError) as exc:
            raise PermissionDenied("A valid organization is required.") from exc
        if not self.request.user.is_superuser and not organization.memberships.filter(
            user=self.request.user, is_active=True, role__in=MANAGER_ROLES
        ).exists():
            raise PermissionDenied("Manager access is required.")
        serializer.save(organization=organization, created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
