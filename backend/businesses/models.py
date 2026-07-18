from django.db import models

from core.models import BaseModel
from organizations.models import Organization


class EducationBusiness(BaseModel):
    class BusinessType(models.TextChoices):
        ONLINE_ACADEMY = "online_academy", "Online academy"
        CORPORATE_TRAINING = "corporate_training", "Corporate training"
        CHURCH_MINISTRY = "church_ministry", "Church or ministry school"
        TRADE_SCHOOL = "trade_school", "Trade school"
        COACHING = "coaching", "Coaching business"
        CERTIFICATION = "certification", "Certification program"
        MEMBERSHIP = "membership", "Membership community"
        CUSTOM = "custom", "Custom"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="education_businesses")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    business_type = models.CharField(max_length=40, choices=BusinessType.choices)
    mission = models.TextField(blank=True)
    target_audience = models.TextField(blank=True)
    transformation_promise = models.TextField(blank=True)
    delivery_model = models.JSONField(default=dict, blank=True)
    revenue_model = models.JSONField(default=dict, blank=True)
    blueprint = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "slug"], name="unique_business_slug_per_org")
        ]

    def __str__(self):
        return f"{self.name} — {self.organization.name}"
