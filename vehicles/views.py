from rest_framework import viewsets
from core.permissions import IsTenantAdmin
from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    """GET/POST /api/vehicles/ — Vehicle management."""
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs

    def perform_destroy(self, instance):
        # Business Rule: Vehicle cannot be deleted if assigned (current_driver exists)
        if hasattr(instance, 'current_driver') and instance.current_driver:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Vehicle cannot be deleted if assigned to a driver.")
        super().perform_destroy(instance)
