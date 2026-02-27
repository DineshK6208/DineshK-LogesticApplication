import json
import uuid
import hmac
import hashlib
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.test import Client
from shipments.models import Shipment
from payments.models import Payment
from tenants.models import Tenant
from accounts.models import User
from webhooks.models import WebhookEndpoint, ReceivedWebhook

class Command(BaseCommand):
    help = 'Runs a test suite for the webhook module (inbound and outbound).'

    def add_arguments(self, parser):
        parser.add_argument('--inbound', action='store_true', help='Test inbound payment webhook')
        parser.add_argument('--outbound', action='store_true', help='Test outbound shipment webhook')
        parser.add_argument('--tracking', type=str, help='Specific tracking number to use')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Webhook Test Runner ---'))

        # Ensure we have a tenant and shipment for testing
        tenant = Tenant.objects.first()
        if not tenant:
            tenant = Tenant.objects.create(name="Test Logistics", slug="test-logistics")
            self.stdout.write(f"Created test tenant: {tenant.name}")

        tracking_number = options.get('tracking') or f"TEST-{uuid.uuid4().hex[:8].upper()}"
        
        shipment, created = Shipment.objects.get_or_create(
            tracking_number=tracking_number,
            defaults={
                'tenant': tenant,
                'sender_name': 'Test Sender',
                'receiver_name': 'Test Receiver',
                'status': 'created'
            }
        )
        if created:
            self.stdout.write(f"Created test shipment: {tracking_number}")

        payment, created = Payment.objects.get_or_create(
            shipment=shipment,
            defaults={
                'tenant': tenant,
                'amount': 100.00,
                'mode': 'online',
                'status': 'pending'
            }
        )
        if created:
            self.stdout.write(f"Created test payment for {tracking_number}")

        if options['inbound']:
            self._test_inbound_payment(shipment, payment)
        
        if options['outbound']:
            self._test_outbound_trigger(shipment)

        if not options['inbound'] and not options['outbound']:
            self.stdout.write("Please specify --inbound or --outbound to run a test.")

    def _test_inbound_payment(self, shipment, payment):
        self.stdout.write(self.style.MIGRATE_HEADING("\nTesting Inbound Webhook (Razorpay Simulation)..."))
        
        payload = {
            'event': 'payment.success',
            'event_id': f"razor_{uuid.uuid4().hex}",
            'tracking_number': shipment.tracking_number,
            'razorpay_payment_id': f"pay_{uuid.uuid4().hex[:10]}"
        }
        body = json.dumps(payload)
        
        # Calculate signature if secret exists
        secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
        signature = ""
        if secret:
            signature = hmac.new(
                secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()

        client = Client()
        response = client.post(
            '/api/webhooks/payment/',
            data=body,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=signature
        )

        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS("✓ Webhook accepted by API"))
            
            # Verify processing
            payment.refresh_from_db()
            if payment.status == 'completed':
                self.stdout.write(self.style.SUCCESS(f"✓ Payment status updated to: {payment.status}"))
            else:
                self.stdout.write(self.style.WARNING(f"✗ Payment status is still: {payment.status}"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ Webhook failed with status {response.status_code}: {response.content}"))

    def _test_outbound_trigger(self, shipment):
        self.stdout.write(self.style.MIGRATE_HEADING("\nTesting Outbound Webhook Trigger..."))
        
        # Check if any endpoints are registered
        endpoints = WebhookEndpoint.objects.all()
        if not endpoints.exists():
            self.stdout.write(self.style.WARNING("! No outbound WebhookEndpoints found. Register one in the Admin or via API first."))
            return

        from webhooks.trigger import trigger_webhook
        
        self.stdout.write(f"Triggering 'shipment.status_updated' for {shipment.tracking_number}...")
        logs = trigger_webhook(
            event='shipment.status_updated',
            payload={
                'tracking_number': shipment.tracking_number,
                'status': 'in_transit'
            },
            tenant=shipment.tenant
        )

        if logs:
            for log in logs:
                status_icon = "✓" if log.delivery_status == 'success' else "✗"
                self.stdout.write(f"{status_icon} Delivered to {log.endpoint.url} - Status: {log.delivery_status}")
        else:
            self.stdout.write(self.style.WARNING("! No active endpoints subscribed to 'shipment.status_updated' event."))
