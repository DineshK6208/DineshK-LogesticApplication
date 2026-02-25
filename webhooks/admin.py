from django.contrib import admin
from .models import WebhookEndpoint, WebhookLog, ReceivedWebhook


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_active', 'events', 'tenant', 'created_at')
    list_filter = ('is_active', 'tenant')
    search_fields = ('url',)


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = (
        'event', 'endpoint', 'delivery_status', 'status_code',
        'attempts', 'max_retries', 'next_retry_at', 'timestamp',
    )
    list_filter = ('delivery_status', 'event')
    search_fields = ('event', 'error_message')
    readonly_fields = ('payload', 'error_message', 'timestamp')


@admin.register(ReceivedWebhook)
class ReceivedWebhookAdmin(admin.ModelAdmin):
    list_display = ('source', 'event_id', 'event_type', 'status', 'received_at')
    list_filter = ('source', 'status', 'event_type')
    search_fields = ('event_id', 'event_type')
    readonly_fields = ('payload', 'signature', 'received_at', 'processed_at')
