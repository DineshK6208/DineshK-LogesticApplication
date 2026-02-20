from django.db import models
from core.models import TenantAwareModel


class WebhookEndpoint(TenantAwareModel):
    """Configuration for external webhook notifications."""
    url = models.URLField()
    secret = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    events = models.JSONField(default=list, help_text="List of events to trigger for (e.g. shipment.delivered)")

    def __str__(self):
        return f"Webhook: {self.url}"


class WebhookLog(TenantAwareModel):
    """Log of triggered webhooks and their delivery status."""
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='logs')
    event = models.CharField(max_length=100)
    payload = models.JSONField()
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    attempts = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event} -> {self.endpoint.url} ({self.status_code})"
