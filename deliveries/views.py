from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsDriverOrAdmin, IsTenantAdmin
from core.utils import create_audit_log
from .models import (
    DeliveryAttempt, DeliveryConfig,
    ItemRequest, ItemPayment, DeliveryTracking,
)
from .serializers import (
    DeliveryAttemptSerializer,
    DeliveryConfigSerializer,
    ProofUploadSerializer,
    ItemRequestCreateSerializer,
    ItemRequestListSerializer,
    ItemPaymentProcessSerializer,
    DeliveryTrackingSerializer,
    DeliveryTrackingUpdateSerializer,
)


# ──────────────────────────────────────────────────────────────
# Delivery Attempt Views (existing)
# ──────────────────────────────────────────────────────────────

class DeliveryAttemptViewSet(viewsets.ModelViewSet):
    """
    GET/POST /api/attempts/ — Delivery attempt management.

    Business rules enforced on creation:
    - Auto-calculates attempt_number.
    - Rejects creation if max attempts already reached.
    - On success → marks shipment as 'delivered'.
    - On failure at max → marks shipment as 'rto'.
    - On failure below max → marks shipment as 'delivery_failed'.
    """

    queryset = DeliveryAttempt.objects.select_related('shipment').all()
    serializer_class = DeliveryAttemptSerializer
    permission_classes = [IsDriverOrAdmin]
    filterset_fields = ['shipment', 'status']
    search_fields = ['shipment__tracking_number']
    ordering_fields = ['attempt_number', 'timestamp']

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)

        shipment_id = self.request.query_params.get('shipment_id')
        if shipment_id:
            qs = qs.filter(shipment_id=shipment_id)

        return qs

    def perform_create(self, serializer):
        """Core business logic for recording a delivery attempt."""
        shipment = serializer.validated_data['shipment']
        tenant = getattr(self.request, 'tenant', shipment.tenant)

        last_attempt = (
            DeliveryAttempt.objects
            .filter(shipment=shipment)
            .order_by('-attempt_number')
            .first()
        )
        attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1

        attempt = serializer.save(
            attempt_number=attempt_number,
            tenant=tenant,
        )

        attempt_status = attempt.status
        max_attempts = DeliveryConfig.get_max_attempts(tenant)

        if attempt_status == 'success':
            shipment.status = 'delivered'
            shipment.delivered_at = timezone.now()
            shipment.save(update_fields=['status', 'delivered_at'])
        elif attempt_status == 'failed':
            if attempt_number >= max_attempts:
                shipment.status = 'rto'
                shipment.save(update_fields=['status'])
            else:
                shipment.status = 'delivery_failed'
                shipment.save(update_fields=['status'])

        self._create_audit_log(attempt, shipment)

    def _create_audit_log(self, attempt, shipment):
        try:
            create_audit_log(
                user=self.request.user,
                action='delivery_attempt',
                entity_type='DeliveryAttempt',
                entity_id=attempt.id,
                changes={
                    'shipment': str(shipment.tracking_number),
                    'attempt_number': attempt.attempt_number,
                    'status': attempt.status,
                    'reason': attempt.reason,
                },
                tenant=getattr(self.request, 'tenant', None),
            )
        except Exception:
            pass

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """GET /api/attempts/{id}/history/ — All attempts for the same shipment."""
        attempt = self.get_object()
        related_attempts = DeliveryAttempt.objects.filter(
            shipment=attempt.shipment,
        ).order_by('attempt_number')
        serializer = self.get_serializer(related_attempts, many=True)
        return Response(serializer.data)


class ProofUploadView(generics.UpdateAPIView):
    """
    PATCH /api/attempts/<uuid:attempt_id>/upload-proof/
    Upload proof image and/or signature to an existing delivery attempt.
    """

    queryset = DeliveryAttempt.objects.all()
    serializer_class = ProofUploadSerializer
    permission_classes = [IsDriverOrAdmin]
    lookup_url_kwarg = 'attempt_id'

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs

    def patch(self, request, *args, **kwargs):
        attempt = self.get_object()
        serializer = ProofUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        proof_image = serializer.validated_data.get('proof_image')
        signature = serializer.validated_data.get('signature')

        if proof_image:
            attempt.proof_image = proof_image
        if signature:
            attempt.signature = signature
        attempt.save(update_fields=[
            f for f in ['proof_image', 'signature']
            if serializer.validated_data.get(f)
        ])

        return Response({
            'status': 'Proof uploaded successfully',
            'attempt_id': str(attempt.id),
            'proof_image': attempt.proof_image.url if attempt.proof_image else None,
            'signature': attempt.signature.url if attempt.signature else None,
        })


class DeliveryConfigViewSet(viewsets.ModelViewSet):
    """CRUD /api/delivery-config/ — Per-tenant delivery configuration."""

    queryset = DeliveryConfig.objects.all()
    serializer_class = DeliveryConfigSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        serializer.save(tenant=tenant)


# ──────────────────────────────────────────────────────────────
# Item Request & Delivery Tracking Views
# ──────────────────────────────────────────────────────────────

class ItemRequestViewSet(viewsets.ModelViewSet):
    """
    GET/POST /api/item-requests/ — Item request management.

    POST creates an item request with nested items and receiver details,
    auto-generates request_number, calculates total, and creates a
    pending payment record.
    """

    queryset = ItemRequest.objects.select_related(
        'receiver', 'payment', 'tracking',
    ).prefetch_related('items').all()
    permission_classes = [IsDriverOrAdmin]

    def get_serializer_class(self):
        if self.action in ('create',):
            return ItemRequestCreateSerializer
        return ItemRequestListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        # Customers see only their own requests
        if hasattr(self.request.user, 'role') and self.request.user.role == 'customer':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        serializer.save(user=self.request.user, tenant=tenant)

        # Audit log
        try:
            item_request = serializer.instance
            create_audit_log(
                user=self.request.user,
                action='item_request_created',
                entity_type='ItemRequest',
                entity_id=item_request.id,
                changes={
                    'request_number': item_request.request_number,
                    'total_amount': str(item_request.total_amount),
                    'items_count': item_request.items.count(),
                },
                tenant=tenant,
            )
        except Exception:
            pass

    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        """
        POST /api/item-requests/{id}/pay/ — Process payment.

        On success:
        - Updates payment status to 'completed'
        - Updates item request status to 'paid'
        - Creates DeliveryTracking with status 'pending'
        """
        item_request = self.get_object()

        # Validate request is in payable state
        if item_request.status != 'pending_payment':
            return Response(
                {'error': f'Cannot pay for request in "{item_request.status}" status.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ItemPaymentProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_method = serializer.validated_data['payment_method']
        transaction_id = serializer.validated_data.get('transaction_id', '')

        # Update payment record
        try:
            payment = item_request.payment
        except ItemPayment.DoesNotExist:
            return Response(
                {'error': 'No payment record found for this request.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.payment_method = payment_method
        payment.transaction_id = transaction_id
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.save(update_fields=[
            'payment_method', 'transaction_id', 'status', 'paid_at',
        ])

        # Update item request status
        item_request.status = 'paid'
        item_request.save(update_fields=['status'])

        # Create delivery tracking
        tenant = getattr(request, 'tenant', item_request.tenant)
        DeliveryTracking.objects.create(
            item_request=item_request,
            tenant=tenant,
            status='pending',
        )

        # Audit log
        try:
            create_audit_log(
                user=request.user,
                action='payment_completed',
                entity_type='ItemPayment',
                entity_id=payment.id,
                changes={
                    'request_number': item_request.request_number,
                    'amount': str(payment.amount),
                    'payment_method': payment_method,
                    'transaction_id': transaction_id,
                },
                tenant=tenant,
            )
        except Exception:
            pass

        return Response({
            'status': 'Payment successful',
            'request_number': item_request.request_number,
            'amount_paid': str(payment.amount),
            'payment_method': payment_method,
            'delivery_status': 'pending',
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'patch'], url_path='tracking')
    def tracking(self, request, pk=None):
        """
        GET /api/item-requests/{id}/tracking/ — View delivery tracking.
        PATCH /api/item-requests/{id}/tracking/ — Update delivery status.

        Status transitions: pending → in_transit → delivered.
        On 'delivered': records delivery location and timestamp.
        """
        item_request = self.get_object()

        try:
            tracking = item_request.tracking
        except DeliveryTracking.DoesNotExist:
            return Response(
                {'error': 'Delivery tracking not started. Payment must be completed first.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == 'GET':
            serializer = DeliveryTrackingSerializer(tracking)
            return Response(serializer.data)

        # PATCH — update tracking status
        serializer = DeliveryTrackingUpdateSerializer(
            data=request.data,
            context={'tracking': tracking},
        )
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        current_location = serializer.validated_data.get('current_location', '')
        delivery_lat = serializer.validated_data.get('delivery_latitude')
        delivery_lng = serializer.validated_data.get('delivery_longitude')

        tracking.status = new_status
        update_fields = ['status']

        if current_location:
            tracking.current_location = current_location
            update_fields.append('current_location')

        if new_status == 'in_transit':
            item_request.status = 'in_delivery'
            item_request.save(update_fields=['status'])

        if new_status == 'delivered':
            tracking.delivered_at = timezone.now()
            update_fields.append('delivered_at')

            if delivery_lat is not None:
                tracking.delivery_latitude = delivery_lat
                update_fields.append('delivery_latitude')
            if delivery_lng is not None:
                tracking.delivery_longitude = delivery_lng
                update_fields.append('delivery_longitude')

            item_request.status = 'delivered'
            item_request.save(update_fields=['status'])

        tracking.save(update_fields=update_fields)

        # Audit log
        try:
            create_audit_log(
                user=request.user,
                action='delivery_status_update',
                entity_type='DeliveryTracking',
                entity_id=tracking.id,
                changes={
                    'request_number': item_request.request_number,
                    'new_status': new_status,
                    'location': current_location,
                },
                tenant=getattr(request, 'tenant', None),
            )
        except Exception:
            pass

        return Response(DeliveryTrackingSerializer(tracking).data)
