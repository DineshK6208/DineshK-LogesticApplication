from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'amount', 'mode', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'mode', 'tenant')
    search_fields = ('shipment__tracking_number', 'transaction_id')
