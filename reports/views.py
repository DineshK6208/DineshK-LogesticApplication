from rest_framework import views, status, serializers
from rest_framework.response import Response
from core.permissions import IsTenantAdmin, IsOperationsManager
from shipments.models import Shipment


class DashboardSummaryView(views.APIView):
    """GET /api/dashboard/summary/ — Main dashboard metrics."""
    permission_classes = [IsOperationsManager]

    def get(self, request, *args, **kwargs):
        # Mock summary data
        return Response({
            "total_shipments": 1050,
            "delivered": 920,
            "in_transit": 80,
            "cancelled": 25,
            "rto": 15,
            "delivery_failed": 10,
            "success_rate": "87.6%"
        })


class ShipmentReportView(views.APIView):
    """GET /api/reports/shipments/ — Detailed shipment analytics."""
    permission_classes = [IsOperationsManager]

    def get(self, request, *args, **kwargs):
        return Response({
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
            "data": [200, 250, 180, 220, 300]
        })


class RevenueReportView(views.APIView):
    """GET /api/reports/revenue/ — Revenue summary."""
    permission_classes = [IsTenantAdmin]

    def get(self, request, *args, **kwargs):
        return Response({
            "total_revenue": 150000.00,
            "refunded": 2500.00,
            "net_revenue": 147500.00,
            "currency": "USD"
        })
