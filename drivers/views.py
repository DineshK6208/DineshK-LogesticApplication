from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import IsTenantAdmin, IsDriver, IsOperationsManager
from .models import Driver, KYCDocument, DriverLocation
from .serializers import DriverSerializer, KYCDocumentSerializer, DriverLocationSerializer
from shipments.serializers import ShipmentSerializer


class DriverViewSet(viewsets.ModelViewSet):
    """GET/POST /api/drivers/ — Driver management."""
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs

    @action(detail=True, methods=['patch'], permission_classes=[IsDriver | IsTenantAdmin])
    def availability(self, request, pk=None):
        """PATCH /api/drivers/{id}/availability/ — Update online status."""
        driver = self.get_object()
        is_available = request.data.get('is_available')
        if is_available is None:
            return Response({"error": "is_available required"}, status=status.HTTP_400_BAD_REQUEST)
        driver.is_available = is_available
        driver.save()
        return Response(self.get_serializer(driver).data)

    @action(detail=True, methods=['get'], permission_classes=[IsDriver | IsOperationsManager])
    def assigned_shipments(self, request, pk=None):
        """GET /api/drivers/{id}/assigned-shipments/ — From Driver Mobile APIs document."""
        driver = self.get_object()
        from shipments.models import Shipment
        shipments = Shipment.objects.filter(driver=driver).exclude(status__in=['delivered', 'cancelled', 'rto'])
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)


class DriverLocationView(generics.CreateAPIView):
    """POST /api/drivers/{id}/location/ — Record real-time location."""
    serializer_class = DriverLocationSerializer
    permission_classes = [IsDriver]

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


class KYCUploadView(generics.CreateAPIView):
    """POST /api/upload/kyc-document/ — Driver Mobile document upload."""
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsDriver | IsTenantAdmin]

    def perform_create(self, serializer):
        # In a real app, find driver by request.user
        driver = Driver.objects.get(user=self.request.user)
        serializer.save(driver=driver, tenant=self.request.tenant)
