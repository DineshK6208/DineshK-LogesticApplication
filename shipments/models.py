from django.db import models
from core.models import TenantAwareModel


class Shipment(TenantAwareModel):
    """Core shipment entity with status lifecycle."""
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('rto', 'RTO'),
        ('delivery_failed', 'Delivery Failed'),
    ]

    tracking_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='created')
    sender_name = models.CharField(max_length=255)
    sender_address = models.TextField()
    receiver_name = models.CharField(max_length=255)
    receiver_address = models.TextField()
    driver = models.ForeignKey(
        'drivers.Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments'
    )
    scheduled_date = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.tracking_number} ({self.status})"

    class Meta(TenantAwareModel.Meta):
        verbose_name = 'Shipment'


class Parcel(TenantAwareModel):
    """Multiple parcels within a single shipment."""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='parcels')
    description = models.CharField(max_length=255)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    dimensions = models.CharField(max_length=100, blank=True, help_text="LxWxH")

    def __str__(self):
        return f"Parcel for {self.shipment.tracking_number}"
