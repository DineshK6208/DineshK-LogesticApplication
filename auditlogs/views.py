from rest_framework import generics
from core.permissions import IsSuperAdmin, IsTenantAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(generics.ListAPIView):
    """GET /api/audit-logs/ — Immutable action logs."""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsTenantAdmin]
    filterset_fields = ['entity_type', 'entity_id', 'action']
    search_fields = ['entity_id', 'action']

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs
