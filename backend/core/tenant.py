from django.db.models import QuerySet

from organizations.models import OrganizationMembership

MANAGER_ROLES = {
    OrganizationMembership.Role.OWNER,
    OrganizationMembership.Role.ADMINISTRATOR,
}
AUTHOR_ROLES = MANAGER_ROLES | {OrganizationMembership.Role.INSTRUCTOR}
REVIEW_ROLES = AUTHOR_ROLES | {OrganizationMembership.Role.REVIEWER}


def active_memberships(user) -> QuerySet:
    if not user or not user.is_authenticated:
        return OrganizationMembership.objects.none()
    return OrganizationMembership.objects.filter(user=user, is_active=True, organization__is_active=True)


def organization_ids_for(user):
    if getattr(user, "is_superuser", False):
        return None
    return active_memberships(user).values_list("organization_id", flat=True)


def has_organization_role(user, organization, roles) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    return active_memberships(user).filter(organization=organization, role__in=roles).exists()
