import uuid
from django.db import models


class BaseModel(models.Model):
    """Abstract base model with UUID primary key and timestamps."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class TenantAwareModel(BaseModel):
    """Abstract model that scopes data to a tenant."""
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
    )

    class Meta(BaseModel.Meta):
        abstract = True
