from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel


class User(AbstractUser):
    """Custom user with role and tenant association."""

    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('tenant_admin', 'Tenant Admin'),
        ('operations_manager', 'Operations Manager'),
        ('driver', 'Driver'),
        ('finance_manager', 'Finance Manager'),
        ('customer', 'Customer'),
    ]

    id = models.UUIDField(primary_key=True, default=__import__('uuid').uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='customer')
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    is_active = models.BooleanField(default=True)

    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.email} ({self.role})"


class Role(BaseModel):
    """Custom role with dynamic permissions."""
    name = models.CharField(max_length=100)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='roles',
    )
    permissions = models.JSONField(default=list, help_text="List of permission strings")
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('name', 'tenant')
        ordering = ['name']

    def __str__(self):
        return self.name
