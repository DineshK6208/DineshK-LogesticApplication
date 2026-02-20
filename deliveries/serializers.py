from rest_framework import serializers
from .models import DeliveryAttempt


class DeliveryAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAttempt
        fields = ['id', 'shipment', 'attempt_number', 'status', 'reason', 'proof_image', 'timestamp']
        read_only_fields = ['id', 'timestamp']
