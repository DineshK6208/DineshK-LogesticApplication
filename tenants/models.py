from django.db import models
from core.models import BaseModel


class Tenant(BaseModel):
    """Multi-tenant entity representing a company/client."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
