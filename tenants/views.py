from rest_framework import viewsets
from core.permissions import IsSuperAdmin
from .models import Tenant
from .serializers import TenantSerializer


class TenantViewSet(viewsets.ModelViewSet):
    """GET/POST /api/tenants/ — Super Admin only."""
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsSuperAdmin]
    lookup_field = 'id'
