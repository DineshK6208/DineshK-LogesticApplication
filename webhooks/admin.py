from django.contrib import admin
from .models import WebhookEndpoint, WebhookLog, ReceivedWebhook


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_active', 'tenant', 'created_at')
    list_filter = ('is_active', 'tenant')
    search_fields = ('url',)


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'event', 'status_code', 'attempts', 'timestamp')
    list_filter = ('event', 'status_code')


@admin.register(ReceivedWebhook)
class ReceivedWebhookAdmin(admin.ModelAdmin):
    list_display = ('source', 'event_id', 'event_type', 'status', 'received_at')
    list_filter = ('source', 'status', 'event_type')
    search_fields = ('event_id', 'event_type')
    readonly_fields = ('payload', 'signature', 'received_at', 'processed_at')
