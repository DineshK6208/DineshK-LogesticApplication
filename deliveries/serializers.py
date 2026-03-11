import uuid

from rest_framework import serializers
from .models import (
    DeliveryAttempt, DeliveryConfig,
    ItemRequest, RequestItem, ReceiverDetail,
    ItemPayment, DeliveryTracking,
)


# ──────────────────────────────────────────────────────────────
# Delivery Attempt Serializers (existing)
# ──────────────────────────────────────────────────────────────

class DeliveryAttemptSerializer(serializers.ModelSerializer):
    """Serializer for recording and displaying delivery attempts."""

    shipment_tracking_number = serializers.CharField(
        source='shipment.tracking_number', read_only=True,
    )

    class Meta:
        model = DeliveryAttempt
        fields = [
            'id', 'shipment', 'shipment_tracking_number',
            'attempt_number', 'status', 'reason', 'notes',
            'proof_image', 'signature', 'timestamp',
            'latitude', 'longitude',
        ]
        read_only_fields = ['id', 'attempt_number', 'timestamp']

    def validate(self, attrs):
        status_val = attrs.get('status')
        reason = attrs.get('reason', '')

        if status_val == 'failed' and not reason.strip():
            raise serializers.ValidationError({
                'reason': 'A reason is required when the delivery attempt fails.',
            })

        if self.instance is None:
            shipment = attrs.get('shipment')
            if shipment:
                tenant = getattr(shipment, 'tenant', None)
                max_attempts = DeliveryConfig.get_max_attempts(tenant)
                current_count = DeliveryAttempt.objects.filter(shipment=shipment).count()
                if current_count >= max_attempts:
                    raise serializers.ValidationError({
                        'shipment': (
                            f'Maximum delivery attempts ({max_attempts}) '
                            f'reached for this shipment. Shipment is marked for RTO.'
                        ),
                    })

        return attrs


class ProofUploadSerializer(serializers.Serializer):
    """Serializer for uploading proof (image/signature) to an existing attempt."""

    proof_image = serializers.ImageField(required=False)
    signature = serializers.ImageField(required=False)

    def validate(self, attrs):
        if not attrs.get('proof_image') and not attrs.get('signature'):
            raise serializers.ValidationError(
                'At least one of proof_image or signature must be provided.',
            )
        return attrs


class DeliveryConfigSerializer(serializers.ModelSerializer):
    """Serializer for per-tenant delivery configuration."""

    class Meta:
        model = DeliveryConfig
        fields = ['id', 'tenant', 'max_delivery_attempts', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ──────────────────────────────────────────────────────────────
# Item Request & Delivery Tracking Serializers
# ──────────────────────────────────────────────────────────────

class RequestItemSerializer(serializers.ModelSerializer):
    """Serializer for individual items in a request."""

    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = RequestItem
        fields = ['id', 'name', 'description', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['id']


class ReceiverDetailSerializer(serializers.ModelSerializer):
    """Serializer for receiver information."""

    class Meta:
        model = ReceiverDetail
        fields = [
            'id', 'receiver_name', 'contact_number', 'delivery_address',
            'city', 'state', 'postal_code',
        ]
        read_only_fields = ['id']


class ItemPaymentSerializer(serializers.ModelSerializer):
    """Serializer for item request payments."""

    class Meta:
        model = ItemPayment
        fields = [
            'id', 'item_request', 'amount', 'payment_method',
            'status', 'transaction_id', 'paid_at', 'created_at',
        ]
        read_only_fields = ['id', 'amount', 'paid_at', 'created_at']


class ItemPaymentProcessSerializer(serializers.Serializer):
    """Serializer for processing a payment against an item request."""

    payment_method = serializers.ChoiceField(
        choices=['online', 'cod', 'wallet'],
    )
    transaction_id = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        payment_method = attrs.get('payment_method')
        transaction_id = attrs.get('transaction_id', '')

        if payment_method == 'online' and not transaction_id.strip():
            raise serializers.ValidationError({
                'transaction_id': 'Transaction ID is required for online payments.',
            })
        return attrs


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    """Serializer for delivery tracking status."""

    request_number = serializers.CharField(
        source='item_request.request_number', read_only=True,
    )

    class Meta:
        model = DeliveryTracking
        fields = [
            'id', 'item_request', 'request_number', 'status',
            'current_location', 'estimated_delivery_date',
            'delivered_at', 'delivery_latitude', 'delivery_longitude',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'item_request', 'delivered_at', 'created_at', 'updated_at']


class DeliveryTrackingUpdateSerializer(serializers.Serializer):
    """Serializer for updating delivery tracking status with validation."""

    VALID_TRANSITIONS = {
        'pending': ['in_transit'],
        'in_transit': ['delivered'],
        'delivered': [],
    }

    status = serializers.ChoiceField(choices=['pending', 'in_transit', 'delivered'])
    current_location = serializers.CharField(required=False, allow_blank=True, default='')
    delivery_latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True,
    )
    delivery_longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True,
    )

    def validate_status(self, value):
        """Enforce valid status transitions."""
        tracking = self.context.get('tracking')
        if tracking:
            allowed = self.VALID_TRANSITIONS.get(tracking.status, [])
            if value not in allowed:
                raise serializers.ValidationError(
                    f'Cannot transition from "{tracking.status}" to "{value}". '
                    f'Allowed: {allowed or "none (terminal state)"}.'
                )
        return value

    def validate(self, attrs):
        """Require location when marking as delivered."""
        if attrs.get('status') == 'delivered':
            if not attrs.get('current_location', '').strip():
                raise serializers.ValidationError({
                    'current_location': 'Delivery location is required when marking as delivered.',
                })
        return attrs


class ItemRequestCreateSerializer(serializers.ModelSerializer):
    """
    Create an item request with nested items and receiver details in one POST.
    """

    items = RequestItemSerializer(many=True)
    receiver = ReceiverDetailSerializer()

    class Meta:
        model = ItemRequest
        fields = ['id', 'request_number', 'status', 'total_amount', 'notes', 'items', 'receiver']
        read_only_fields = ['id', 'request_number', 'status', 'total_amount']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        receiver_data = validated_data.pop('receiver')

        # Auto-generate request number
        request_number = f"REQ-{uuid.uuid4().hex[:8].upper()}"

        item_request = ItemRequest.objects.create(
            request_number=request_number,
            **validated_data,
        )

        # Create items
        tenant = validated_data.get('tenant', item_request.tenant)
        for item_data in items_data:
            RequestItem.objects.create(
                item_request=item_request,
                tenant=tenant,
                **item_data,
            )

        # Create receiver
        ReceiverDetail.objects.create(
            item_request=item_request,
            tenant=tenant,
            **receiver_data,
        )

        # Calculate total
        item_request.calculate_total()

        # Auto-create pending payment
        ItemPayment.objects.create(
            item_request=item_request,
            tenant=tenant,
            amount=item_request.total_amount,
            payment_method='online',
            status='pending',
        )

        return item_request


class ItemRequestListSerializer(serializers.ModelSerializer):
    """Read-only serializer with all nested details."""

    items = RequestItemSerializer(many=True, read_only=True)
    receiver = ReceiverDetailSerializer(read_only=True)
    payment = ItemPaymentSerializer(read_only=True)
    tracking = DeliveryTrackingSerializer(read_only=True)

    class Meta:
        model = ItemRequest
        fields = [
            'id', 'request_number', 'status', 'total_amount', 'notes',
            'items', 'receiver', 'payment', 'tracking',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields
