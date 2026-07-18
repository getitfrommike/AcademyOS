from django.conf import settings
from django.db import models

from core.models import UUIDModel
from organizations.models import Organization


class AuditEvent(UUIDModel):
    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        PUBLISH = "publish", "Publish"
        PERMISSION_CHANGE = "permission_change", "Permission change"
        SECURITY_EVENT = "security_event", "Security event"

    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    action = models.CharField(max_length=40, choices=Action.choices)
    resource_type = models.CharField(max_length=100, blank=True)
    resource_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "created_at"]), models.Index(fields=["action", "created_at"])]

    def __str__(self):
        return f"{self.get_action_display()} — {self.resource_type or 'platform'}"
