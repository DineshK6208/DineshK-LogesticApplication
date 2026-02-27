from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsTenantAdmin, IsDriver, IsOperationsManager, IsFinanceManager
from shipments.models import Shipment
from shipments.serializers import ShipmentSerializer
from deliveries.models import DeliveryAttempt
from deliveries.serializers import DeliveryAttemptSerializer
from earnings.models import Earning
from earnings.serializers import EarningSerializer

from .models import Driver, KYCDocument, DriverLocation
from .serializers import DriverSerializer, KYCDocumentSerializer, DriverLocationSerializer


class DriverViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Driver management.
    Includes specialized actions for the Driver Mobile App.
    """
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs

    @action(detail=False, methods=['get'], permission_classes=[IsDriver])
    def me(self, request):
        """GET /api/drivers/me/ — Get current driver profile."""
        try:
            driver = Driver.objects.get(user=request.user)
            serializer = self.get_serializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response({"error": "Driver profile not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'], permission_classes=[IsDriver | IsTenantAdmin])
    def availability(self, request, pk=None):
        """PATCH /api/drivers/{id}/availability/ — Update online status."""
        driver = self.get_object()
        
        # Security: Drivers can only update their own status
        if request.user.role == 'driver' and driver.user != request.user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        is_available = request.data.get('is_available')
        if is_available is None:
            return Response({"error": "is_available required"}, status=status.HTTP_400_BAD_REQUEST)
        
        driver.is_available = is_available
        driver.save(update_fields=['is_available'])
        return Response(self.get_serializer(driver).data)

    @action(detail=True, methods=['get'], permission_classes=[IsDriver | IsOperationsManager])
    def assigned_shipments(self, request, pk=None):
        """GET /api/drivers/{id}/assigned-shipments/ — View active tasks."""
        driver = self.get_object()
        shipments = Shipment.objects.filter(driver=driver).exclude(
            status__in=['delivered', 'cancelled', 'rto']
        ).order_by('-created_at')
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsDriver | IsOperationsManager])
    def update_shipment_status(self, request, pk=None):
        """
        POST /api/drivers/{id}/update-shipment-status/
        Updates the status of a specific shipment assigned to the driver.
        Payload: {"shipment_id": "...", "status": "..."}
        """
        driver = self.get_object()
        shipment_id = request.data.get('shipment_id')
        new_status = request.data.get('status')

        try:
            shipment = Shipment.objects.get(id=shipment_id, driver=driver)
            shipment.status = new_status
            if new_status == 'delivered':
                shipment.delivered_at = timezone.now()
            shipment.save()
            return Response(ShipmentSerializer(shipment).data)
        except Shipment.DoesNotExist:
            return Response({"error": "Shipment not found or not assigned to you"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsDriver | IsOperationsManager])
    def record_attempt(self, request, pk=None):
        """
        POST /api/drivers/{id}/record-attempt/
        Logs a delivery attempt (failed or successful).
        Payload: {"shipment_id": "...", "status": "failed", "reason": "..."}
        """
        driver = self.get_object()
        shipment_id = request.data.get('shipment_id')
        
        try:
            shipment = Shipment.objects.get(id=shipment_id, driver=driver)
            attempts_count = shipment.attempts.count() + 1
            
            data = request.data.copy()
            data['shipment'] = shipment.id
            data['attempt_number'] = attempts_count
            
            serializer = DeliveryAttemptSerializer(data=data)
            if serializer.is_valid():
                # Attach tenant from request (from TenantMiddleware)
                serializer.save(tenant=request.tenant)
                
                # Update shipment status based on attempt
                if request.data.get('status') == 'failed':
                    shipment.status = 'delivery_failed'
                    shipment.save(update_fields=['status'])
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Shipment.DoesNotExist:
            return Response({"error": "Shipment not found or not assigned to you"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], permission_classes=[IsDriver | IsFinanceManager])
    def earnings(self, request, pk=None):
        """GET /api/drivers/{id}/earnings/ — View driver income records."""
        driver = self.get_object()
        earnings = Earning.objects.filter(driver=driver).order_by('-calculated_at')
        serializer = EarningSerializer(earnings, many=True)
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
        # Find driver profile associated with the current user
        try:
            driver = Driver.objects.get(user=self.request.user)
            serializer.save(driver=driver, tenant=self.request.tenant)
        except Driver.DoesNotExist:
            # Fallback or error handling for users without a driver profile
            pass
