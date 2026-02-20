from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import IsFinanceManager
from .models import Payment
from .serializers import PaymentSerializer, RefundSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """GET/POST /api/payments/ — Payment management."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsFinanceManager]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """POST /api/payments/{id}/refund/ — Process refund."""
        payment = self.get_object()
        if payment.status != 'completed':
            return Response({"error": "Only completed payments can be refunded."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment.status = 'refunded'
        payment.save()
        return Response({"status": "Refund processed", "payment_id": payment.id})


class PaymentWebhookView(generics.GenericAPIView):
    """POST /api/payments/webhook/ — Handle external payment webhooks."""
    permission_classes = [] # External provider hits this

    def post(self, request, *args, **kwargs):
        # In a real app, verify signature and update payment status
        return Response({"status": "success"})
