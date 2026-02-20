from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'tenant', 'vehicle_number', 'vehicle_type', 'capacity_kg', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_vehicle_number(self, value):
        if Vehicle.objects.filter(vehicle_number=value).exists():
            raise serializers.ValidationError("Vehicle number must be unique.")
        return value
