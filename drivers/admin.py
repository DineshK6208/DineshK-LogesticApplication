from django.contrib import admin
from .models import Driver, KYCDocument, DriverLocation


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'kyc_status', 'is_available', 'tenant')
    list_filter = ('kyc_status', 'is_available', 'tenant')
    search_fields = ('user__email', 'license_number')


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ('driver', 'document_type', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'document_type')


@admin.register(DriverLocation)
class DriverLocationAdmin(admin.ModelAdmin):
    list_display = ('driver', 'latitude', 'longitude', 'timestamp')
    list_filter = ('driver',)
    

