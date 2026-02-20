from django.db import models
from core.models import TenantAwareModel


class AuditLog(TenantAwareModel):
    """Immutable log of critical system actions."""
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50) # create, update, delete, status_change
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=255)
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        # Immutable rule (business logic should enforce no updates/deletes)

    def __str__(self):
        return f"{self.user} - {self.action} {self.entity_type} ({self.entity_id})"
