import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from academies.models import Academy
from organizations.models import Organization


class Program(models.Model):
    """
    A structured learning product offered through an academy.

    Examples:
    - AI Business Accelerator
    - Python Developer Program
    - Cybersecurity Professional Track
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="programs",
    )

    academy = models.ForeignKey(
        Academy,
        on_delete=models.CASCADE,
        related_name="programs",
    )

    name = models.CharField(
        max_length=200,
    )

    slug = models.SlugField(
        max_length=200,
    )

    short_description = models.CharField(
        max_length=300,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    is_featured = models.BooleanField(
        default=False,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programs_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programs_updated",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

        verbose_name = "Program"
        verbose_name_plural = "Programs"

        constraints = [
            models.UniqueConstraint(
                fields=["academy", "slug"],
                name="unique_program_slug_per_academy",
            ),
        ]

        indexes = [
            models.Index(
                fields=["organization", "status"],
                name="program_org_status_idx",
            ),
            models.Index(
                fields=["academy", "status"],
                name="program_academy_status_idx",
            ),
            models.Index(
                fields=["organization", "is_featured"],
                name="program_org_featured_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} — {self.academy.name}"

    def clean(self) -> None:
        """
        Ensure that the selected academy belongs to the selected
        organization.
        """
        super().clean()

        if (
            self.academy_id
            and self.organization_id
            and self.academy.organization_id != self.organization_id
        ):
            raise ValidationError(
                {
                    "academy": (
                        "The selected academy must belong to the "
                        "program's organization."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
