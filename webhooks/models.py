from django.db import models
from core.models import TenantAwareModel, BaseModel


class WebhookEndpoint(TenantAwareModel):
    """Configuration for external webhook notifications."""
    url = models.URLField()
    secret = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    events = models.JSONField(
        default=list,
        help_text="List of events to trigger for (e.g. shipment.delivered)",
    )

    def __str__(self):
        return f"Webhook: {self.url}"


class WebhookLog(TenantAwareModel):
    """Log of triggered webhooks and their delivery status."""
    endpoint = models.ForeignKey(
        WebhookEndpoint, on_delete=models.CASCADE, related_name='logs',
    )
    event = models.CharField(max_length=100)
    payload = models.JSONField()
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    attempts = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event} -> {self.endpoint.url} ({self.status_code})"


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
