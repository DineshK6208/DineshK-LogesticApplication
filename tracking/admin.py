from django.contrib import admin
from .models import TrackingEvent


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'status', 'location', 'timestamp')
    list_filter = ('status',)
    search_fields = ('shipment__tracking_number', 'location')
