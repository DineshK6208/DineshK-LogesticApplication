from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_number', 'vehicle_type', 'capacity_kg', 'is_active', 'tenant')
    list_filter = ('vehicle_type', 'is_active', 'tenant')
    search_fields = ('vehicle_number',)
