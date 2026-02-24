from django.contrib import admin
from .models import Earning, Payout


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ('driver', 'shipment', 'amount', 'calculated_at')
    list_filter = ('tenant',)
    search_fields = ('driver__user__email', 'shipment__tracking_number')


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('driver', 'amount', 'status', 'processed_at')
    list_filter = ('status', 'tenant')
    search_fields = ('driver__user__email',)
