from rest_framework import serializers
from .models import Shipment, Parcel


class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ['id', 'shipment', 'description', 'weight_kg', 'dimensions']
        read_only_fields = ['id']


class ShipmentSerializer(serializers.ModelSerializer):
    parcels = ParcelSerializer(many=True, read_only=True)
    driver_name = serializers.SerializerMethodField()
    
    # Aliases for frontend compatibility
    origin_address = serializers.CharField(source='sender_address', read_only=True)
    destination_address = serializers.CharField(source='receiver_address', read_only=True)
    customer_name = serializers.CharField(source='receiver_name', read_only=True)
    estimated_delivery_at = serializers.DateTimeField(source='scheduled_date', read_only=True)
    weight = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_number', 'status', 'sender_name', 'sender_address',
            'receiver_name', 'receiver_address', 'driver', 'driver_name',
            'scheduled_date', 'delivered_at', 'parcels', 'created_at',
            'origin_address', 'destination_address', 'customer_name', 
            'estimated_delivery_at', 'weight'
        ]
        read_only_fields = ['id', 'tracking_number', 'created_at', 'delivered_at']

    def get_driver_name(self, obj):
        if obj.driver and obj.driver.user:
            return obj.driver.user.get_full_name()
        return ""

    def get_weight(self, obj):
        # Sum weight from parcels if they exist
        total_weight = sum(p.weight_kg for p in obj.parcels.all())
        return f"{total_weight} kg" if total_weight > 0 else "N/A"


class BulkShipmentSerializer(serializers.Serializer):
    shipments = ShipmentSerializer(many=True)


class RateCalculationSerializer(serializers.Serializer):
    weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    origin_zip = serializers.CharField()
    destination_zip = serializers.CharField()
