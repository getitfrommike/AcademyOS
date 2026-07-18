import uuid

from django.conf import settings
from django.db import models


class Organization(models.Model):
    """
    A customer, company, nonprofit, school, or brand using AcademyOS.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="OrganizationMembership",
        related_name="organizations",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class OrganizationMembership(models.Model):
    """
    Connects a user to an organization with a role.

    A single user may belong to multiple organizations and may have a
    different role in each organization.
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMINISTRATOR = "administrator", "Administrator"
        INSTRUCTOR = "instructor", "Instructor"
        REVIEWER = "reviewer", "Reviewer"
        STUDENT = "student", "Student"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    is_active = models.BooleanField(default=True)

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["organization__name", "user__email"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_user_membership_per_organization",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.email} — {self.organization.name} ({self.get_role_display()})"