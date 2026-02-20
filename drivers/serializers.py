from rest_framework import serializers
from .models import Driver, KYCDocument, DriverLocation
from accounts.serializers import UserSerializer


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ['id', 'document_type', 'file', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']


class DriverSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    kyc_documents = KYCDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'user', 'user_details', 'tenant', 'license_number', 'kyc_status', 'is_available', 'current_vehicle', 'kyc_documents']
        read_only_fields = ['id', 'kyc_status']


class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = ['id', 'driver', 'latitude', 'longitude', 'timestamp']
        read_only_fields = ['id', 'timestamp']
