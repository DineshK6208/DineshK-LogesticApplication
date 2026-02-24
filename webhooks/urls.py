from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WebhookEndpointViewSet,
    WebhookLogListView,
    ReceivedWebhookListView,
    PaymentWebhookView,
    ShipmentWebhookView,
)

router = DefaultRouter()
router.register(r'webhooks', WebhookEndpointViewSet)

urlpatterns = [
    # ── Management endpoints (authenticated) ──────────
    path('webhooks/logs/', WebhookLogListView.as_view(), name='webhook-logs'),
    path('webhooks/received/', ReceivedWebhookListView.as_view(), name='webhook-received'),

    # ── Receiver endpoints (public, signature-protected) ──
    path('webhooks/payment/', PaymentWebhookView.as_view(), name='webhook-payment'),
    path('webhooks/shipment/', ShipmentWebhookView.as_view(), name='webhook-shipment'),

    # ── Router URLs ───────────────────────────────────
    path('', include(router.urls)),
]
