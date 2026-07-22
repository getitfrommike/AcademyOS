from __future__ import annotations

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Workspace(models.Model):
    """
    A private workspace owned by one authenticated user.

    Every KnowledgeSource and KnowledgeAnalysis must belong to a workspace.
    Ownership checks will be enforced again at the API layer.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="knowledge_workspaces",
    )
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
            models.Index(fields=["owner", "created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_workspace_name_per_owner",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class KnowledgeSource(models.Model):
    """
    Security and lifecycle record for an uploaded source file.

    The original upload must remain quarantined until validation and malware
    scanning succeed. The database stores a relative storage key, not an
    absolute filesystem path.
    """

    class Status(models.TextChoices):
        QUARANTINED = "quarantined", "Quarantined"
        VALIDATING = "validating", "Validating"
        REJECTED = "rejected", "Rejected"
        SCANNING = "scanning", "Scanning"
        READY_FOR_EXTRACTION = (
            "ready_for_extraction",
            "Ready for extraction",
        )
        EXTRACTING = "extracting", "Extracting"
        ANALYZING = "analyzing", "Analyzing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        DELETED = "deleted", "Deleted"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="knowledge_sources",
    )

    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(
        max_length=255,
        unique=True,
        help_text="Random server-generated filename. Never use the client filename.",
    )
    storage_key = models.CharField(
        max_length=500,
        unique=True,
        help_text=(
            "Relative key beneath the private upload root. "
            "Do not store an absolute operating-system path."
        ),
    )

    file_extension = models.CharField(max_length=20)
    declared_mime_type = models.CharField(
        max_length=127,
        blank=True,
    )
    detected_mime_type = models.CharField(
        max_length=127,
        blank=True,
    )

    file_size_bytes = models.BigIntegerField(
        validators=[MinValueValidator(0)],
    )
    sha256 = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Lowercase hexadecimal SHA-256 digest.",
    )

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.QUARANTINED,
        db_index=True,
    )

    rejection_reason = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)

    validation_started_at = models.DateTimeField(null=True, blank=True)
    validation_completed_at = models.DateTimeField(null=True, blank=True)

    malware_scan_started_at = models.DateTimeField(null=True, blank=True)
    malware_scan_completed_at = models.DateTimeField(null=True, blank=True)

    extraction_started_at = models.DateTimeField(null=True, blank=True)
    extraction_completed_at = models.DateTimeField(null=True, blank=True)

    analysis_started_at = models.DateTimeField(null=True, blank=True)
    analysis_completed_at = models.DateTimeField(null=True, blank=True)

    original_file_deleted_at = models.DateTimeField(null=True, blank=True)
    temporary_text_deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["workspace", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(file_size_bytes__gte=0),
                name="knowledge_source_file_size_nonnegative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.original_filename} — {self.get_status_display()}"


class KnowledgeAnalysis(models.Model):
    """
    Retained product generated from a KnowledgeSource.

    Do not store raw uploaded files or unrestricted temporary extracted text
    here. This model is intended for structured, generated products that the
    application is authorized to retain.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    source = models.OneToOneField(
        KnowledgeSource,
        on_delete=models.CASCADE,
        related_name="analysis",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    knowledge_profile = models.JSONField(default=dict, blank=True)
    opportunity_map = models.JSONField(default=dict, blank=True)
    builder_recommendations = models.JSONField(default=list, blank=True)

    engine_version = models.CharField(
        max_length=64,
        blank=True,
        help_text="Version of the Knowledge Engine that generated this record.",
    )

    failure_reason = models.TextField(blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Analysis for {self.source.original_filename}"