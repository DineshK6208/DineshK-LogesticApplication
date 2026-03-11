from django.contrib import admin
from .models import (
    DeliveryAttempt, DeliveryConfig,
    ItemRequest, RequestItem, ReceiverDetail,
    ItemPayment, DeliveryTracking,
)


# ── Delivery Attempt Admin ───────────────────────────────
@admin.register(DeliveryAttempt)
class DeliveryAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'shipment', 'attempt_number', 'status', 'reason', 'timestamp',
    )
    list_filter = ('status', 'timestamp')
    search_fields = ('shipment__tracking_number', 'reason')
    readonly_fields = ('timestamp', 'proof_image', 'signature')
    ordering = ('-timestamp',)


@admin.register(DeliveryConfig)
class DeliveryConfigAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'max_delivery_attempts', 'created_at')
    list_filter = ('max_delivery_attempts',)
    search_fields = ('tenant__name',)


# ── Item Request Admin ───────────────────────────────────
class RequestItemInline(admin.TabularInline):
    model = RequestItem
    extra = 1
    fields = ('name', 'description', 'quantity', 'unit_price')


class ReceiverDetailInline(admin.StackedInline):
    model = ReceiverDetail
    extra = 0
    max_num = 1
    fields = ('receiver_name', 'contact_number', 'delivery_address', 'city', 'state', 'postal_code')


class ItemPaymentInline(admin.StackedInline):
    model = ItemPayment
    extra = 0
    max_num = 1
    readonly_fields = ('paid_at',)


class DeliveryTrackingInline(admin.StackedInline):
    model = DeliveryTracking
    extra = 0
    max_num = 1
    readonly_fields = ('delivered_at',)


@admin.register(ItemRequest)
class ItemRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('request_number', 'user__email')
    readonly_fields = ('request_number', 'total_amount', 'created_at', 'updated_at')
    inlines = [RequestItemInline, ReceiverDetailInline, ItemPaymentInline, DeliveryTrackingInline]
    ordering = ('-created_at',)


@admin.register(ReceiverDetail)
class ReceiverDetailAdmin(admin.ModelAdmin):
    list_display = ('receiver_name', 'contact_number', 'item_request', 'city')
    search_fields = ('receiver_name', 'contact_number', 'item_request__request_number')


@admin.register(ItemPayment)
class ItemPaymentAdmin(admin.ModelAdmin):
    list_display = ('item_request', 'amount', 'payment_method', 'status', 'paid_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('item_request__request_number', 'transaction_id')
    readonly_fields = ('paid_at',)


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('item_request', 'status', 'current_location', 'delivered_at')
    list_filter = ('status',)
    search_fields = ('item_request__request_number', 'current_location')
    readonly_fields = ('delivered_at',)
