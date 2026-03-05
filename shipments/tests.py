from django.test import TestCase
from accounts.models import User, Role
from tenants.models import Tenant
from drivers.models import Driver
from shipments.models import Shipment, Parcel
from shipments.serializers import ShipmentSerializer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

class ShipmentSerializerTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Tenant", slug="test-tenant")
        self.role = Role.objects.create(name="driver", tenant=self.tenant)
        self.user = User.objects.create_user(
            username="driver_user",
            email="driver@example.com", 
            password="password",
            first_name="John",
            last_name="Doe",
            role=self.role,
            tenant=self.tenant
        )
        self.driver = Driver.objects.create(user=self.user, tenant=self.tenant)
        
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.tenant = self.tenant

    def test_shipment_without_driver_serialization(self):
        shipment = Shipment.objects.create(
            tracking_number="TRK-101",
            sender_name="Sender",
            sender_address="Sender Address",
            receiver_name="Receiver",
            receiver_address="Receiver Address",
            tenant=self.tenant
        )
        serializer = ShipmentSerializer(shipment)
        data = serializer.data
        
        self.assertEqual(data['driver_name'], "")
        self.assertEqual(data['origin_address'], "Sender Address")
        self.assertEqual(data['destination_address'], "Receiver Address")
        self.assertEqual(data['customer_name'], "Receiver")
        self.assertEqual(data['weight'], "N/A")

    def test_shipment_with_driver_serialization(self):
        shipment = Shipment.objects.create(
            tracking_number="TRK-102",
            sender_name="Sender",
            sender_address="Sender Address",
            receiver_name="Receiver",
            receiver_address="Receiver Address",
            driver=self.driver,
            tenant=self.tenant
        )
        serializer = ShipmentSerializer(shipment)
        data = serializer.data
        
        self.assertEqual(data['driver_name'], "John Doe")
        self.assertEqual(data['origin_address'], "Sender Address")

    def test_shipment_with_parcels_weight_calculation(self):
        shipment = Shipment.objects.create(
            tracking_number="TRK-103",
            sender_name="Sender",
            sender_address="Sender Address",
            receiver_name="Receiver",
            receiver_address="Receiver Address",
            tenant=self.tenant
        )
        Parcel.objects.create(shipment=shipment, weight_kg=10.5, tenant=self.tenant)
        Parcel.objects.create(shipment=shipment, weight_kg=5.0, tenant=self.tenant)
        
        serializer = ShipmentSerializer(shipment)
        data = serializer.data
        
        self.assertEqual(data['weight'], "15.50 kg")
