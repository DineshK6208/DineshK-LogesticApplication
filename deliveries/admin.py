from django.contrib import admin
from .models import DeliveryAttempt


@admin.register(DeliveryAttempt)
class DeliveryAttemptAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'attempt_number', 'status', 'timestamp')
    list_filter = ('status',)
    search_fields = ('shipment__tracking_number',)
