from django.db import models
from core.models import TenantAwareModel
from core.utils import proof_upload_path


class DeliveryAttempt(TenantAwareModel):
    """Record of a delivery attempt."""
    shipment = models.ForeignKey('shipments.Shipment', on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=[('failed', 'Failed'), ('success', 'Success')])
    reason = models.CharField(max_length=255, blank=True)
    proof_image = models.ImageField(upload_to=proof_upload_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt {self.attempt_number} for {self.shipment.tracking_number}"
