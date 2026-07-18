import uuid

from django.db import models

from organizations.models import Organization


class Academy(models.Model):
    """
    A branded learning environment operated by an organization.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    business = models.ForeignKey(
        "businesses.EducationBusiness",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="academies",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="academies",
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=200,
    )

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

    def __str__(self) -> str:
        return f"{self.name} — {self.organization.name}"