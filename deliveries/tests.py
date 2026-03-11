from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status as http_status
import uuid

from accounts.models import User
from tenants.models import Tenant
from shipments.models import Shipment
from deliveries.models import (
    DeliveryAttempt, DeliveryConfig,
    ItemRequest, RequestItem, ReceiverDetail,
    ItemPayment, DeliveryTracking,
)


class DeliveryAttemptTestCase(TestCase):
    """Tests for delivery attempt recording & business rules."""

    def setUp(self):
        uid = uuid.uuid4().hex[:6]
        self.tenant = Tenant.objects.create(name='Test Tenant', slug=f'test-{uid}')
        self.user = User.objects.create_user(
            username=f'driver_{uid}',
            email=f'driver_{uid}@example.com',
            password='testpass123',
            role='driver',
        )
        self.user.tenant = self.tenant
        self.user.save()

        self.shipment = Shipment.objects.create(
            tracking_number=f'TRK-{uid}',
            sender_name='Sender',
            sender_address='123 Sender St',
            receiver_name='Receiver',
            receiver_address='456 Receiver Ave',
            status='out_for_delivery',
            tenant=self.tenant,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_X_TENANT_ID=str(self.tenant.id))

    def test_attempt_auto_numbering(self):
        r1 = self.client.post('/api/attempts/', {
            'shipment': str(self.shipment.id),
            'status': 'failed',
            'reason': 'Customer not home',
        }, format='json')
        self.assertEqual(r1.status_code, http_status.HTTP_201_CREATED, r1.data)
        self.assertEqual(r1.data['attempt_number'], 1)

        r2 = self.client.post('/api/attempts/', {
            'shipment': str(self.shipment.id),
            'status': 'failed',
            'reason': 'Wrong address',
        }, format='json')
        self.assertEqual(r2.status_code, http_status.HTTP_201_CREATED, r2.data)
        self.assertEqual(r2.data['attempt_number'], 2)

    def test_failed_attempt_requires_reason(self):
        r = self.client.post('/api/attempts/', {
            'shipment': str(self.shipment.id),
            'status': 'failed',
            'reason': '',
        }, format='json')
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertIn('reason', r.data)

    def test_max_attempts_blocks_creation(self):
        for i in range(3):
            self.client.post('/api/attempts/', {
                'shipment': str(self.shipment.id),
                'status': 'failed',
                'reason': f'Failure reason {i + 1}',
            }, format='json')

        r = self.client.post('/api/attempts/', {
            'shipment': str(self.shipment.id),
            'status': 'failed',
            'reason': 'One more try',
        }, format='json')
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)

    def test_auto_rto_after_max_attempts(self):
        for i in range(3):
            self.client.post('/api/attempts/', {
                'shipment': str(self.shipment.id),
                'status': 'failed',
                'reason': f'Fail {i + 1}',
            }, format='json')

        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, 'rto')

    def test_successful_delivery_marks_delivered(self):
        r = self.client.post('/api/attempts/', {
            'shipment': str(self.shipment.id),
            'status': 'success',
        }, format='json')
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED)

        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, 'delivered')
        self.assertIsNotNone(self.shipment.delivered_at)

    def test_configurable_max_attempts(self):
        DeliveryConfig.objects.create(
            tenant=self.tenant,
            max_delivery_attempts=2,
        )
        for i in range(2):
            self.client.post('/api/attempts/', {
                'shipment': str(self.shipment.id),
                'status': 'failed',
                'reason': f'Fail {i + 1}',
            }, format='json')

        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, 'rto')


# ──────────────────────────────────────────────────────────────
# Item Request, Payment & Delivery Tracking Tests
# ──────────────────────────────────────────────────────────────

class ItemRequestFlowTestCase(TestCase):
    """Tests for the complete item request → payment → delivery flow."""

    def setUp(self):
        uid = uuid.uuid4().hex[:6]
        self.tenant = Tenant.objects.create(name='Test Tenant', slug=f'test-ir-{uid}')
        self.user = User.objects.create_user(
            username=f'user_{uid}',
            email=f'user_{uid}@example.com',
            password='testpass123',
            role='driver',
        )
        self.user.tenant = self.tenant
        self.user.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_X_TENANT_ID=str(self.tenant.id))

        self.request_data = {
            'items': [
                {'name': 'Laptop', 'description': 'Dell XPS 15', 'quantity': 1, 'unit_price': '85000.00'},
                {'name': 'Mouse', 'description': 'Wireless Mouse', 'quantity': 2, 'unit_price': '500.00'},
            ],
            'receiver': {
                'receiver_name': 'Dinesh Kumar',
                'contact_number': '+91-9876543210',
                'delivery_address': '42 Marina Beach Road, Chennai',
                'city': 'Chennai',
                'state': 'Tamil Nadu',
                'postal_code': '600001',
            },
            'notes': 'Handle with care',
        }

    # ── Test 1: Create item request with nested data ─────
    def test_create_item_request(self):
        """POST creates request + items + receiver + pending payment."""
        r = self.client.post('/api/item-requests/', self.request_data, format='json')
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)

        # Verify request number is auto-generated
        self.assertTrue(r.data['request_number'].startswith('REQ-'))

        # Verify total is calculated (85000 + 2*500 = 86000)
        self.assertEqual(str(r.data['total_amount']), '86000.00')

        # Verify items stored
        self.assertEqual(len(r.data['items']), 2)

        # Verify receiver stored
        self.assertEqual(r.data['receiver']['receiver_name'], 'Dinesh Kumar')
        self.assertEqual(r.data['receiver']['contact_number'], '+91-9876543210')

        # Verify status is pending_payment
        self.assertEqual(r.data['status'], 'pending_payment')

    # ── Test 2: Items required validation ────────────────
    def test_create_request_requires_items(self):
        """POST without items → 400."""
        data = {**self.request_data, 'items': []}
        r = self.client.post('/api/item-requests/', data, format='json')
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)

    # ── Test 3: Payment triggers delivery ────────────────
    def test_payment_triggers_delivery_tracking(self):
        """Payment completion → status=paid, tracking created as pending."""
        # Create request
        r = self.client.post('/api/item-requests/', self.request_data, format='json')
        request_id = r.data['id']

        # Process payment
        r2 = self.client.post(f'/api/item-requests/{request_id}/pay/', {
            'payment_method': 'online',
            'transaction_id': 'TXN-12345',
        }, format='json')
        self.assertEqual(r2.status_code, http_status.HTTP_200_OK, r2.data)
        self.assertEqual(r2.data['delivery_status'], 'pending')

        # Verify item request status
        item_req = ItemRequest.objects.get(id=request_id)
        self.assertEqual(item_req.status, 'paid')

        # Verify payment record
        self.assertEqual(item_req.payment.status, 'completed')
        self.assertIsNotNone(item_req.payment.paid_at)

        # Verify tracking created
        self.assertEqual(item_req.tracking.status, 'pending')

    # ── Test 4: Delivery tracking status transitions ─────
    def test_delivery_status_transitions(self):
        """pending → in_transit → delivered with location."""
        # Create + pay
        r = self.client.post('/api/item-requests/', self.request_data, format='json')
        request_id = r.data['id']
        self.client.post(f'/api/item-requests/{request_id}/pay/', {
            'payment_method': 'online',
            'transaction_id': 'TXN-99999',
        }, format='json')

        # Move to in_transit
        r2 = self.client.patch(f'/api/item-requests/{request_id}/tracking/', {
            'status': 'in_transit',
            'current_location': 'Chennai Distribution Center',
        }, format='json')
        self.assertEqual(r2.status_code, http_status.HTTP_200_OK, r2.data)
        self.assertEqual(r2.data['status'], 'in_transit')

        # Verify item request status
        item_req = ItemRequest.objects.get(id=request_id)
        self.assertEqual(item_req.status, 'in_delivery')

        # Move to delivered with location
        r3 = self.client.patch(f'/api/item-requests/{request_id}/tracking/', {
            'status': 'delivered',
            'current_location': '42 Marina Beach Road, Chennai',
            'delivery_latitude': '13.047662',
            'delivery_longitude': '80.283049',
        }, format='json')
        self.assertEqual(r3.status_code, http_status.HTTP_200_OK, r3.data)
        self.assertEqual(r3.data['status'], 'delivered')
        self.assertIsNotNone(r3.data['delivered_at'])

        # Verify final state
        item_req.refresh_from_db()
        self.assertEqual(item_req.status, 'delivered')

    # ── Test 5: Invalid status transition ────────────────
    def test_invalid_status_transition_rejected(self):
        """Cannot skip in_transit and go directly to delivered."""
        r = self.client.post('/api/item-requests/', self.request_data, format='json')
        request_id = r.data['id']
        self.client.post(f'/api/item-requests/{request_id}/pay/', {
            'payment_method': 'online',
            'transaction_id': 'TXN-00001',
        }, format='json')

        # Try to skip to delivered
        r2 = self.client.patch(f'/api/item-requests/{request_id}/tracking/', {
            'status': 'delivered',
            'current_location': 'Somewhere',
        }, format='json')
        self.assertEqual(r2.status_code, http_status.HTTP_400_BAD_REQUEST)

    # ── Test 6: Online payment requires transaction_id ───
    def test_online_payment_requires_transaction_id(self):
        """Online payment without transaction_id → 400."""
        r = self.client.post('/api/item-requests/', self.request_data, format='json')
        request_id = r.data['id']

        r2 = self.client.post(f'/api/item-requests/{request_id}/pay/', {
            'payment_method': 'online',
            'transaction_id': '',
        }, format='json')
        self.assertEqual(r2.status_code, http_status.HTTP_400_BAD_REQUEST)

    # ── Test 7: Cannot pay twice ─────────────────────────
    def test_cannot_pay_already_paid_request(self):
        """Paying an already-paid request → 400."""
        r = self.client.post('/api/item-requests/', self.request_data, format='json')
        request_id = r.data['id']

        self.client.post(f'/api/item-requests/{request_id}/pay/', {
            'payment_method': 'online',
            'transaction_id': 'TXN-FIRST',
        }, format='json')

        r2 = self.client.post(f'/api/item-requests/{request_id}/pay/', {
            'payment_method': 'online',
            'transaction_id': 'TXN-SECOND',
        }, format='json')
        self.assertEqual(r2.status_code, http_status.HTTP_400_BAD_REQUEST)

    # ── Test 8: Receiver details stored in DB ────────────
    def test_receiver_details_stored(self):
        """All receiver fields are correctly stored."""
        r = self.client.post('/api/item-requests/', self.request_data, format='json')
        request_id = r.data['id']

        receiver = ReceiverDetail.objects.get(item_request_id=request_id)
        self.assertEqual(receiver.receiver_name, 'Dinesh Kumar')
        self.assertEqual(receiver.contact_number, '+91-9876543210')
        self.assertEqual(receiver.delivery_address, '42 Marina Beach Road, Chennai')
        self.assertEqual(receiver.city, 'Chennai')
        self.assertEqual(receiver.state, 'Tamil Nadu')
        self.assertEqual(receiver.postal_code, '600001')

    # ── Test 9: Delivery location recorded on completion ─
    def test_delivery_location_recorded(self):
        """On delivered, geo-location is stored in the tracking record."""
        r = self.client.post('/api/item-requests/', self.request_data, format='json')
        request_id = r.data['id']
        self.client.post(f'/api/item-requests/{request_id}/pay/', {
            'payment_method': 'wallet',
        }, format='json')

        self.client.patch(f'/api/item-requests/{request_id}/tracking/', {
            'status': 'in_transit',
            'current_location': 'Warehouse',
        }, format='json')

        self.client.patch(f'/api/item-requests/{request_id}/tracking/', {
            'status': 'delivered',
            'current_location': 'Customer doorstep',
            'delivery_latitude': '13.082680',
            'delivery_longitude': '80.270718',
        }, format='json')

        tracking = DeliveryTracking.objects.get(item_request_id=request_id)
        self.assertEqual(tracking.status, 'delivered')
        self.assertIsNotNone(tracking.delivered_at)
        self.assertEqual(float(tracking.delivery_latitude), 13.082680)
        self.assertEqual(float(tracking.delivery_longitude), 80.270718)
