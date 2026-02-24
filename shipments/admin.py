from django.contrib import admin
from .models import Shipment, Parcel


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'status', 'sender_name', 'receiver_name', 'driver', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('tracking_number', 'sender_name', 'receiver_name')
    readonly_fields = ('tracking_number',)


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'description', 'weight_kg', 'dimensions')
    search_fields = ('shipment__tracking_number', 'description')
