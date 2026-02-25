"""
webhooks/views.py
─────────────────
Three sets of views:

1. *Management views* — CRUD for WebhookEndpoint + read WebhookLog
   (existing functionality, requires authentication).

2. *Receiver views* — PaymentWebhookView & ShipmentWebhookView
   (public POST endpoints that accept external webhook calls,
    perform HMAC signature verification, store payloads,
    and dispatch to services.py for processing).

3. *Retry view* — Manually trigger retry of failed outbound webhooks.
"""

import hashlib
import hmac
import json
import logging
import uuid

from django.conf import settings
from django.db import IntegrityError
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsTenantAdmin

from .models import ReceivedWebhook, WebhookEndpoint, WebhookLog
from .serializers import (
    ReceivedWebhookSerializer,
    WebhookEndpointSerializer,
    WebhookLogSerializer,
)
from .services import process_webhook

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════
#  1. Management views (authenticated)
# ══════════════════════════════════════════════

class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """
    CRUD /api/webhooks/ — Register / Delete / Update webhook endpoints.

    POST   → Register a new webhook
    DELETE → Remove a webhook
    GET    → List all webhooks
    PUT    → Update a webhook
    """
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs


class WebhookLogListView(generics.ListAPIView):
    """GET /api/webhooks/logs/ — Webhook delivery history (includes failed logs)."""
    queryset = WebhookLog.objects.all().order_by('-timestamp')
    serializer_class = WebhookLogSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)

        # Optional filter by delivery_status
        delivery_status = self.request.query_params.get('status')
        if delivery_status:
            qs = qs.filter(delivery_status=delivery_status)

        return qs


class ReceivedWebhookListView(generics.ListAPIView):
    """GET /api/webhooks/received/ — Browse stored incoming webhooks."""
    queryset = ReceivedWebhook.objects.all()
    serializer_class = ReceivedWebhookSerializer
    permission_classes = [IsTenantAdmin]


class RetryFailedWebhooksView(APIView):
    """
    POST /api/webhooks/retry/ — Manually retry all failed webhooks.

    Returns the count of retried webhooks.
    """
    permission_classes = [IsTenantAdmin]

    def post(self, request, *args, **kwargs):
        from django.utils import timezone
        from django.db.models import F

        now = timezone.now()
        failed_logs = WebhookLog.objects.filter(
            delivery_status=WebhookLog.DeliveryStatus.FAILED,
            attempts__lt=F('max_retries'),
        ).select_related('endpoint')

        if hasattr(request, 'tenant') and request.tenant:
            failed_logs = failed_logs.filter(tenant=request.tenant)

        retried = 0
        results = []
        for log in failed_logs:
            if not log.endpoint.is_active:
                continue

            from .trigger import _retry_delivery
            _retry_delivery(log)
            retried += 1
            results.append({
                'log_id': str(log.id),
                'event': log.event,
                'delivery_status': log.delivery_status,
                'attempts': log.attempts,
            })

        return Response({
            'retried': retried,
            'results': results,
        }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════
#  2. Receiver views (public — signature-protected)
# ══════════════════════════════════════════════

class BaseWebhookReceiverView(APIView):
    """
    Abstract base for receiving webhooks from external providers.

    Subclasses set:
        source          – ReceivedWebhook.Source value
        secret_setting  – settings key that holds the HMAC secret
        signature_header – HTTP header name carrying the signature
    """

    authentication_classes = []          # no auth — external call
    permission_classes = [AllowAny]      # open endpoint
    source: str = ''
    secret_setting: str = ''
    signature_header: str = ''

    # ── helpers ────────────────────────────────

    def _get_secret(self) -> str:
        return getattr(settings, self.secret_setting, '')

    def _get_signature(self, request) -> str:
        return request.META.get(
            f'HTTP_{self.signature_header.upper().replace("-", "_")}', ''
        )

    def _verify_signature(self, payload_bytes: bytes, received_sig: str) -> bool:
        """HMAC-SHA256 comparison."""
        secret = self._get_secret()
        if not secret:
            # If no secret configured, skip verification (dev mode).
            logger.warning("No webhook secret configured for %s", self.source)
            return True
        expected = hmac.new(
            secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, received_sig)

    def _extract_event_id(self, payload: dict) -> str:
        """Try common keys; fall back to a generated UUID."""
        for key in ('event_id', 'id', 'webhook_id'):
            if key in payload:
                return str(payload[key])
        return str(uuid.uuid4())

    def _extract_event_type(self, payload: dict) -> str:
        for key in ('event', 'event_type', 'type'):
            if key in payload:
                return str(payload[key])
        return 'unknown'

    # ── POST handler ──────────────────────────

    def post(self, request, *args, **kwargs):
        # 1. Read raw body
        payload_bytes = request.body
        received_sig = self._get_signature(request)

        # 2. Signature verification 🔐
        if not self._verify_signature(payload_bytes, received_sig):
            logger.warning("Invalid webhook signature from %s", self.source)
            return Response(
                {'detail': 'Invalid signature.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Parse JSON
        try:
            payload = json.loads(payload_bytes)
        except json.JSONDecodeError:
            return Response(
                {'detail': 'Invalid JSON.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_id = self._extract_event_id(payload)
        event_type = self._extract_event_type(payload)

        # 4. Idempotency check — store payload
        try:
            webhook = ReceivedWebhook.objects.create(
                source=self.source,
                event_id=event_id,
                event_type=event_type,
                payload=payload,
                signature=received_sig,
            )
        except IntegrityError:
            # Duplicate event_id → already received
            logger.info(
                "Duplicate webhook ignored: source=%s event_id=%s",
                self.source,
                event_id,
            )
            return Response({'detail': 'Already received.'}, status=status.HTTP_200_OK)

        # 5. Process event (fast: runs synchronously here;
        #    in production can be dispatched to Celery).
        process_webhook(webhook)

        # 6. Return 200 OK ⚡
        return Response({'detail': 'Webhook received.'}, status=status.HTTP_200_OK)


class PaymentWebhookView(BaseWebhookReceiverView):
    """
    POST /api/webhooks/payment/

    Receives payment events from Razorpay.
    """
    source = ReceivedWebhook.Source.RAZORPAY
    secret_setting = 'RAZORPAY_WEBHOOK_SECRET'
    signature_header = 'X-Razorpay-Signature'


class ShipmentWebhookView(BaseWebhookReceiverView):
    """
    POST /api/webhooks/shipment/

    Receives shipment tracking events from Shiprocket / Delhivery.
    """
    source = ReceivedWebhook.Source.SHIPROCKET
    secret_setting = 'SHIPROCKET_WEBHOOK_SECRET'
    signature_header = 'X-Shiprocket-Signature'
