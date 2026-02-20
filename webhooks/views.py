from rest_framework import viewsets, generics
from core.permissions import IsTenantAdmin
from .models import WebhookEndpoint, WebhookLog
from .serializers import WebhookEndpointSerializer, WebhookLogSerializer


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """GET/POST /api/webhooks/ — Webhook configuration management."""
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs


class WebhookLogListView(generics.ListAPIView):
    """GET /api/webhooks/logs/ — Webhook delivery history."""
    queryset = WebhookLog.objects.all()
    serializer_class = WebhookLogSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs
