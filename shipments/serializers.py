from rest_framework import serializers
from .models import Shipment, Parcel


class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ['id', 'shipment', 'description', 'weight_kg', 'dimensions']
        read_only_fields = ['id']


class ShipmentSerializer(serializers.ModelSerializer):
    parcels = ParcelSerializer(many=True, read_only=True)
    driver_name = serializers.CharField(source='driver.user.get_full_name', read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_number', 'status', 'sender_name', 'sender_address',
            'receiver_name', 'receiver_address', 'driver', 'driver_name',
            'scheduled_date', 'delivered_at', 'parcels', 'created_at'
        ]
        read_only_fields = ['id', 'tracking_number', 'created_at', 'delivered_at']


class BulkShipmentSerializer(serializers.Serializer):
    shipments = ShipmentSerializer(many=True)


class RateCalculationSerializer(serializers.Serializer):
    weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    origin_zip = serializers.CharField()
    destination_zip = serializers.CharField()
