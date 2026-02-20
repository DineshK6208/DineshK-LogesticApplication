from rest_framework import serializers
from .models import TrackingEvent


class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEvent
        fields = ['id', 'status', 'location', 'notes', 'timestamp']
        read_only_fields = ['id', 'timestamp']
