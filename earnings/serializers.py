from rest_framework import serializers
from .models import Earning, Payout


class EarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earning
        fields = ['id', 'driver', 'shipment', 'amount', 'calculated_at']


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ['id', 'driver', 'amount', 'status', 'processed_at', 'created_at']
        read_only_fields = ['id', 'status', 'processed_at', 'created_at']
