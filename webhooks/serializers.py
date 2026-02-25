from rest_framework import serializers
from .models import WebhookEndpoint, WebhookLog, ReceivedWebhook


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ['id', 'url', 'secret', 'is_active', 'events', 'created_at']
        read_only_fields = ['id', 'created_at']


class WebhookLogSerializer(serializers.ModelSerializer):
    endpoint_url = serializers.CharField(source='endpoint.url', read_only=True)

    class Meta:
        model = WebhookLog
        fields = [
            'id', 'endpoint', 'endpoint_url', 'event', 'payload',
            'status_code', 'error_message', 'delivery_status',
            'attempts', 'max_retries', 'next_retry_at', 'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']


class ReceivedWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceivedWebhook
        fields = [
            'id', 'source', 'event_id', 'event_type',
            'payload', 'signature', 'status', 'error_detail',
            'received_at', 'processed_at',
        ]
        read_only_fields = ['id', 'received_at', 'processed_at']
