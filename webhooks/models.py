from django.db import models
from core.models import TenantAwareModel, BaseModel


class WebhookEndpoint(TenantAwareModel):
    """
    Configuration for external webhook notifications.

    Admins register a URL + secret + list of events they want
    to subscribe to.  The trigger service sends POST requests
    to active endpoints whenever a matching event occurs.
    """
    url = models.URLField()
    secret = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    events = models.JSONField(
        default=list,
        help_text="List of events to trigger for (e.g. shipment.status_changed, payment.updated, payout.processed)",
    )

    def __str__(self):
        return f"Webhook: {self.url}"


class WebhookLog(TenantAwareModel):
    """
    Log of every outbound webhook delivery attempt.

    Stores success AND failed deliveries for debugging,
    auditing, and retry support.
    """

    class DeliveryStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    endpoint = models.ForeignKey(
        WebhookEndpoint, on_delete=models.CASCADE, related_name='logs',
    )
    event = models.CharField(max_length=100)
    payload = models.JSONField()
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
    )
    attempts = models.IntegerField(default=0)
    max_retries = models.IntegerField(
        default=3,
        help_text="Maximum number of delivery attempts.",
    )
    next_retry_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta(TenantAwareModel.Meta):
        verbose_name = 'Webhook Log'
        verbose_name_plural = 'Webhook Logs'

    def __str__(self):
        return f"{self.event} -> {self.endpoint.url} ({self.delivery_status})"

    @property
    def can_retry(self) -> bool:
        return (
            self.delivery_status == self.DeliveryStatus.FAILED
            and self.attempts < self.max_retries
        )


# ──────────────────────────────────────────────────────────────
# Received Webhook — stores incoming payloads from external
# providers (Razorpay, Shiprocket, Delhivery, etc.)
# ──────────────────────────────────────────────────────────────

class ReceivedWebhook(BaseModel):
    """
    Stores every incoming webhook payload.

    Fields:
        source       – provider name (razorpay / shiprocket / delhivery)
        event_id     – unique ID from the provider (idempotency key)
        event_type   – e.g. payment.success, shipment.delivered
        payload      – full raw JSON body
        signature    – signature header sent by provider
        status       – processing lifecycle (received → processed / failed)
        error_detail – error message if processing failed
    """

    class Source(models.TextChoices):
        RAZORPAY = 'razorpay', 'Razorpay'
        SHIPROCKET = 'shiprocket', 'Shiprocket'
        DELHIVERY = 'delhivery', 'Delhivery'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        RECEIVED = 'received', 'Received'
        PROCESSED = 'processed', 'Processed'
        FAILED = 'failed', 'Failed'

    source = models.CharField(max_length=30, choices=Source.choices)
    event_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique event ID from the provider — used for idempotency.",
    )
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    signature = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
    )
    error_detail = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'Received Webhook'
        verbose_name_plural = 'Received Webhooks'
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['source', 'event_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"[{self.source}] {self.event_type} — {self.status}"
