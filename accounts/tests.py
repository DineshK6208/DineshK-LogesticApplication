from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import uuid

class APIGlobalTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.unique_id = uuid.uuid4().hex[:6]
        self.user_data = {
            "username": f"user_{self.unique_id}",
            "email": f"test_{self.unique_id}@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "role": "super_admin"
        }

    def test_full_flow(self):
        # 1. Register
        # Note: We use the full path. Let's verify URL conf.
        response = self.client.post('/api/auth/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        
        access_token = response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 2. Create Tenant
        tenant_data = {
            "name": "Test Corp",
            "slug": f"test-corp-{self.unique_id}",
            "settings": {"cur": "USD"}
        }
        response = self.client.post('/api/tenants/', tenant_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        tenant_id = response.data['id']

        # 3. Create Shipment
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}', HTTP_X_TENANT_ID=str(tenant_id))
        shipment_data = {
            "sender_name": "Alice",
            "sender_address": "Addr 1",
            "receiver_name": "Bob",
            "receiver_address": "Addr 2"
        }
        response = self.client.post('/api/shipments/', shipment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        tracking_number = response.data['tracking_number']

        # 4. Public Track
        self.client.credentials() # Clear auth
        response = self.client.get(f'/api/public/track/{tracking_number}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['current_status'], 'created')
