from django.conf import settings
from django.db import models
from core.models import TenantAwareModel
from core.utils import proof_upload_path


def signature_upload_path(instance, filename):
    """Generate upload path for delivery signatures."""
    import os
    return os.path.join('uploads', 'delivery_signatures', str(instance.shipment_id), filename)


class DeliveryAttempt(TenantAwareModel):
    """Record of a delivery attempt with proof and geo-location."""

    STATUS_CHOICES = [
        ('failed', 'Failed'),
        ('success', 'Success'),
    ]

    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    attempt_number = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    reason = models.CharField(
        max_length=255,
        blank=True,
        help_text='Required when status is "failed".',
    )
    notes = models.TextField(blank=True, help_text='Additional driver notes.')
    proof_image = models.ImageField(upload_to=proof_upload_path, null=True, blank=True)
    signature = models.ImageField(upload_to=signature_upload_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Geo-location (future enhancement — not enforced)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text='Latitude of delivery attempt location.',
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text='Longitude of delivery attempt location.',
    )

    class Meta(TenantAwareModel.Meta):
        unique_together = ('shipment', 'attempt_number')
        ordering = ['attempt_number']

    def __str__(self):
        try:
            return f"Attempt {self.attempt_number} for {self.shipment.tracking_number}"
        except AttributeError:
            return f"Attempt {self.attempt_number} (ID: {self.id})"


class DeliveryConfig(TenantAwareModel):
    """Per-tenant delivery configuration."""

    max_delivery_attempts = models.PositiveIntegerField(
        default=3,
        help_text='Maximum delivery attempts before marking shipment as RTO.',
    )

    class Meta(TenantAwareModel.Meta):
        verbose_name = 'Delivery Configuration'
        verbose_name_plural = 'Delivery Configurations'

    def __str__(self):
        return f"Delivery Config for {self.tenant} (max={self.max_delivery_attempts})"

    @classmethod
    def get_max_attempts(cls, tenant):
        """Return max attempts for a tenant, falling back to global setting."""
        try:
            config = cls.objects.get(tenant=tenant)
            return config.max_delivery_attempts
        except cls.DoesNotExist:
            return getattr(settings, 'MAX_DELIVERY_ATTEMPTS', 3)


# ──────────────────────────────────────────────────────────────
# Item Request & Delivery Tracking System
# ──────────────────────────────────────────────────────────────

class ItemRequest(TenantAwareModel):
    """A user's request to purchase and deliver items."""

    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid'),
        ('in_delivery', 'In Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='item_requests',
    )
    request_number = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_payment')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, help_text='Optional notes from the user.')

    class Meta(TenantAwareModel.Meta):
        verbose_name = 'Item Request'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_number} ({self.status})"

    def calculate_total(self):
        """Recalculate total from associated items."""
        from django.db.models import F, Sum
        total = (
            self.items.aggregate(
                total=Sum(F('quantity') * F('unit_price'))
            )['total']
            or 0
        )
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total


class RequestItem(TenantAwareModel):
    """An individual item within an ItemRequest."""

    item_request = models.ForeignKey(
        ItemRequest,
        on_delete=models.CASCADE,
        related_name='items',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta(TenantAwareModel.Meta):
        verbose_name = 'Request Item'

    def __str__(self):
        return f"{self.name} x{self.quantity} (₹{self.unit_price})"

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class ReceiverDetail(TenantAwareModel):
    """Receiver information for an ItemRequest."""

    item_request = models.OneToOneField(
        ItemRequest,
        on_delete=models.CASCADE,
        related_name='receiver',
    )
    receiver_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    delivery_address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    class Meta(TenantAwareModel.Meta):
        verbose_name = 'Receiver Detail'

    def __str__(self):
        return f"{self.receiver_name} — {self.contact_number}"


class ItemPayment(TenantAwareModel):
    """Payment record for an ItemRequest."""

    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online Payment'),
        ('cod', 'Cash on Delivery'),
        ('wallet', 'Wallet'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    item_request = models.OneToOneField(
        ItemRequest,
        on_delete=models.CASCADE,
        related_name='payment',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta(TenantAwareModel.Meta):
        verbose_name = 'Item Payment'

    def __str__(self):
        return f"Payment {self.status} for {self.item_request.request_number}"


class DeliveryTracking(TenantAwareModel):
    """Tracks the delivery lifecycle of an ItemRequest."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]

    item_request = models.OneToOneField(
        ItemRequest,
        on_delete=models.CASCADE,
        related_name='tracking',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_location = models.CharField(
        max_length=255, blank=True,
        help_text='Current location description during transit.',
    )
    estimated_delivery_date = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Geo-location recorded on delivery
    delivery_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
    )
    delivery_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
    )

    class Meta(TenantAwareModel.Meta):
        verbose_name = 'Delivery Tracking'
        verbose_name_plural = 'Delivery Tracking'

    def __str__(self):
        return f"Tracking {self.item_request.request_number} — {self.status}"
