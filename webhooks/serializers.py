from rest_framework import serializers
from .models import WebhookEndpoint, WebhookLog


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ['id', 'url', 'secret', 'is_active', 'events', 'created_at']
        read_only_fields = ['id', 'created_at']


class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = ['id', 'endpoint', 'event', 'payload', 'status_code', 'error_message', 'attempts', 'timestamp']
        read_only_fields = ['id', 'timestamp']
