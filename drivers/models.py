from django.db import models
from core.models import TenantAwareModel
from core.utils import kyc_upload_path


class Driver(TenantAwareModel):
    """Driver profile associated with a user and tenant."""
    KYC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='driver_profile'
    )
    license_number = models.CharField(max_length=50, unique=True)
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='pending')
    is_available = models.BooleanField(default=False)
    current_vehicle = models.OneToOneField(
        'vehicles.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_driver'
    )

    def __str__(self):
        return f"Driver: {self.user.email}"


class KYCDocument(TenantAwareModel):
    """KYC documents uploaded by/for a driver."""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='kyc_documents')
    document_type = models.CharField(max_length=50)
    file = models.FileField(upload_to=kyc_upload_path)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.document_type} for {self.driver.user.email}"


class DriverLocation(TenantAwareModel):
    """Real-time location tracking for drivers."""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
