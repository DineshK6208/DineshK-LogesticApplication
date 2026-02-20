from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'shipment', 'amount', 'mode', 'status', 'transaction_id', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']


class RefundSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
