from django.db import models
from core.models import TenantAwareModel


class TrackingEvent(TenantAwareModel):
    """Event log for shipment tracking."""
    shipment = models.ForeignKey('shipments.Shipment', on_delete=models.CASCADE, related_name='tracking_events')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.tracking_number} -> {self.status} @ {self.timestamp}"
