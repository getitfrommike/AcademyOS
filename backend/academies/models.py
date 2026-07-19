import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Organization


class Academy(models.Model):
    """
    A branded learning environment operated by an organization.

    An academy may optionally belong to an education business, but the
    business and academy must belong to the same organization.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="academies",
    )

    business = models.ForeignKey(
        "businesses.EducationBusiness",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="academies",
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(max_length=200)

    description = models.TextField(blank=True)

    logo_url = models.URLField(blank=True)

    primary_color = models.CharField(
        max_length=20,
        blank=True,
        help_text="Example: #111111",
    )

    secondary_color = models.CharField(
        max_length=20,
        blank=True,
        help_text="Example: #FFD700",
    )

    custom_domain = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: academy.thugcoding.com",
    )

    is_public = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="academies_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="academies_updated",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

        verbose_name = "Academy"
        verbose_name_plural = "Academies"

        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_academy_slug_per_organization",
            ),
        ]

        indexes = [
            models.Index(
                fields=["organization", "is_active"],
                name="academy_org_active_idx",
            ),
            models.Index(
                fields=["organization", "is_public"],
                name="academy_org_public_idx",
            ),
            models.Index(
                fields=["business", "is_active"],
                name="academy_business_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} — {self.organization.name}"

    def clean(self) -> None:
        super().clean()

        if (
            self.business_id
            and self.organization_id
            and self.business.organization_id != self.organization_id
        ):
            raise ValidationError(
                {
                    "business": (
                        "The selected business must belong to the academy's "
                        "organization."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)