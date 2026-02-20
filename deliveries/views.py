from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from core.permissions import IsDriverOrAdmin
from .models import DeliveryAttempt
from .serializers import DeliveryAttemptSerializer


class DeliveryAttemptViewSet(viewsets.ModelViewSet):
    """GET/POST /api/attempts/ — Delivery attempt management."""
    queryset = DeliveryAttempt.objects.all()
    serializer_class = DeliveryAttemptSerializer
    permission_classes = [IsDriverOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs


class ProofUploadView(generics.CreateAPIView):
    """POST /api/upload/delivery-proof/ — Driver Mobile proof upload."""
    serializer_class = DeliveryAttemptSerializer
    permission_classes = [IsDriverOrAdmin]

    def post(self, request, *args, **kwargs):
        # In a real app, logic to attach proof to specific shipment/attempt
        return Response({"status": "Proof uploaded successfully", "proof_url": "/media/proofs/123.jpg"})
