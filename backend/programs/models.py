import uuid

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

    name = models.CharField(max_length=200)

    slug = models.SlugField(max_length=200)

    short_description = models.CharField(
        max_length=300,
        blank=True,
    )

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        default="draft",
    )

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

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

    def __str__(self) -> str:
        return f"{self.name} — {self.academy.name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        """
        Prevent a program from combining an academy and organization
        that do not belong together.
        """
        from django.core.exceptions import ValidationError

        if (
            self.academy_id
            and self.organization_id
            and self.academy.organization_id != self.organization_id
        ):
            raise ValidationError(
                {
                    "organization": (
                        "The selected organization must own the selected academy."
                    )
                }
            )
