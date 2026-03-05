from django.db import models
from core.models import TenantAwareModel


class Earning(TenantAwareModel):
    """Earnings per shipment for drivers."""
    driver = models.ForeignKey('drivers.Driver', on_delete=models.CASCADE, related_name='earnings')
    shipment = models.OneToOneField('shipments.Shipment', on_delete=models.CASCADE, related_name='earning_record')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return f"{self.amount} for {self.driver.user.email} (TRK: {self.shipment.tracking_number})"
        except AttributeError:
            return f"{self.amount} for unknown driver (ID: {self.id})"


class Payout(TenantAwareModel):
    """Payout processing for driver earnings."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]

    driver = models.ForeignKey('drivers.Driver', on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        try:
            return f"Payout {self.amount} to {self.driver.user.email} - {self.status}"
        except AttributeError:
            return f"Payout {self.amount} (ID: {self.id}) - {self.status}"
