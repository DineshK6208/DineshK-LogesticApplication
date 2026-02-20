from django.db import models
from core.models import TenantAwareModel


class Payment(TenantAwareModel):
    """Payment record linked to a shipment."""
    PAYMENT_MODE_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('wallet', 'Wallet'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    shipment = models.OneToOneField('shipments.Shipment', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Payment for {self.shipment.tracking_number} - {self.status}"
