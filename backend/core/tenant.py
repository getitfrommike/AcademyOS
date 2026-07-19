from collections.abc import Collection
from typing import TypeAlias

from django.db.models import QuerySet

from organizations.models import OrganizationMembership


OrganizationIdQuerySet: TypeAlias = QuerySet


# May manage organization-level resources and settings.
MANAGER_ROLES = {
    OrganizationMembership.Role.OWNER,
    OrganizationMembership.Role.ADMINISTRATOR,
}

# May create and edit instructional content.
AUTHOR_ROLES = MANAGER_ROLES | {
    OrganizationMembership.Role.INSTRUCTOR,
}

# May review instructional content in addition to authoring it.
REVIEW_ROLES = AUTHOR_ROLES | {
    OrganizationMembership.Role.REVIEWER,
}


def active_memberships(user) -> QuerySet:
    """
    Return the user's active memberships in active organizations.

    Anonymous, missing, or inactive users receive an empty queryset.
    """
    if (
        user is None
        or not getattr(user, "is_authenticated", False)
        or not getattr(user, "is_active", False)
    ):
        return OrganizationMembership.objects.none()

    return OrganizationMembership.objects.filter(
        user=user,
        is_active=True,
        organization__is_active=True,
    )


def organization_ids_for(user) -> OrganizationIdQuerySet | None:
    """
    Return organization IDs the user may access.

    None means unrestricted organization access and is returned only for
    superusers. All callers must explicitly handle the None case.
    """
    if getattr(user, "is_superuser", False):
        return None

    return active_memberships(user).values_list(
        "organization_id",
        flat=True,
    )


def has_organization_role(
    user,
    organization,
    roles: Collection[str],
) -> bool:
    """
    Return True when the user has one of the supplied roles in the organization.

    Superusers are permitted regardless of membership.
    """
    if getattr(user, "is_superuser", False):
        return True

    if organization is None:
        return False

    return active_memberships(user).filter(
        organization=organization,
        role__in=roles,
    ).exists()