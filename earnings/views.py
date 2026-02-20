from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from core.permissions import IsFinanceManager, IsDriver
from .models import Earning, Payout
from .serializers import EarningSerializer, PayoutSerializer


class EarningViewSet(viewsets.ModelViewSet):
    """GET /api/earnings/ — Driver earnings management."""
    queryset = Earning.objects.all()
    serializer_class = EarningSerializer
    permission_classes = [IsFinanceManager]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'driver':
            qs = qs.filter(driver__user=self.request.user)
        elif hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs


class PayoutViewSet(viewsets.ModelViewSet):
    """GET/POST /api/payouts/ — Payout management."""
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer
    permission_classes = [IsFinanceManager]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'driver':
            qs = qs.filter(driver__user=self.request.user)
        elif hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs


class SettlementReportView(generics.GenericAPIView):
    """GET /api/finance/settlement-report/ — Driver Mobile settlement API."""
    permission_classes = [IsFinanceManager | IsDriver]

    def get(self, request, *args, **kwargs):
        # Mock settlement summary
        return Response({
            "total_earnings": 1500.00,
            "total_paid": 1200.00,
            "pending_settlement": 300.00,
            "currency": "USD"
        })
