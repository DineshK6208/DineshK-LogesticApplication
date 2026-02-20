from django.db import models
from core.models import TenantAwareModel


class Vehicle(TenantAwareModel):
    """Vehicle entity for logistics operations."""
    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Bike'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ]

    vehicle_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vehicle_number} ({self.vehicle_type})"
