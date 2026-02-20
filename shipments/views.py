from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import uuid
from core.permissions import IsOperationsManager, IsDriverOrAdmin
from .models import Shipment, Parcel
from .serializers import ShipmentSerializer, ParcelSerializer, RateCalculationSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    """GET/POST /api/shipments/ — Shipment lifecycle management."""
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsOperationsManager]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs

    def perform_create(self, serializer):
        tracking_number = f"TRK-{uuid.uuid4().hex[:8].upper()}"
        serializer.save(tracking_number=tracking_number, tenant=self.request.tenant)

    @action(detail=True, methods=['post'], permission_classes=[IsOperationsManager])
    def assign(self, request, pk=None):
        """POST /api/shipments/{id}/assign/ — Assign driver to shipment."""
        shipment = self.get_object()
        driver_id = request.data.get('driver_id')
        if not driver_id:
            return Response({"error": "driver_id required"}, status=status.HTTP_400_BAD_REQUEST)
        shipment.driver_id = driver_id
        shipment.status = 'assigned'
        shipment.save()
        return Response(self.get_serializer(shipment).data)

    @action(detail=True, methods=['post'], permission_classes=[IsDriverOrAdmin])
    def pickup_confirm(self, request, pk=None):
        """POST /api/shipments/{id}/pickup-confirm/ — Driver confirms pickup."""
        shipment = self.get_object()
        shipment.status = 'picked_up'
        shipment.save()
        return Response(self.get_serializer(shipment).data)

    @action(detail=True, methods=['post'], permission_classes=[IsDriverOrAdmin])
    def delivery_confirm(self, request, pk=None):
        """POST /api/shipments/{id}/delivery-confirm/ — Driver confirms delivery."""
        shipment = self.get_object()
        shipment.status = 'delivered'
        shipment.delivered_at = timezone.now()
        shipment.save()
        return Response(self.get_serializer(shipment).data)


class ParcelViewSet(viewsets.ModelViewSet):
    """GET/POST /api/parcels/ — Parcel management."""
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer
    permission_classes = [IsOperationsManager]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs


class RateCalculateView(generics.GenericAPIView):
    """POST /api/shipments/calculate-rate/ — Estimate shipping cost."""
    serializer_class = RateCalculationSerializer
    permission_classes = [IsDriverOrAdmin]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Mock calculation: weight * 10 + distance * 5
        rate = float(serializer.validated_data['weight']) * 10 + float(serializer.validated_data.get('distance', 0)) * 5
        return Response({"estimated_rate": rate, "currency": "USD"})


class ShipmentExportView(generics.GenericAPIView):
    """GET /api/shipments/export/ — Export shipment history."""
    permission_classes = [IsOperationsManager]

    def get(self, request, *args, **kwargs):
        # In a real app, generate CSV/Excel
        return Response({"message": "Export started. You will receive an email shortly.", "download_url": "/media/exports/shipments.csv"})
