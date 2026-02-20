from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'is_read', 'notification_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class SendNotificationSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    title = serializers.CharField()
    message = serializers.CharField()
    type = serializers.CharField(required=False)
