from django.db.models.signals import post_save
from django.dispatch import receiver
from shipments.models import Shipment
from .models import Earning

@receiver(post_save, sender=Shipment)
def create_driver_earning(sender, instance, created, **kwargs):
    """
    Automatically create an Earning record when a shipment is marked as delivered.
    """
    if instance.status == 'delivered' and instance.driver:
        # Check if an earning already exists for this shipment to avoid duplicates
        if not Earning.objects.filter(shipment=instance).exists():
            # Basic earning logic: Fixed amount per delivery for now
            # In a real app, this might depend on distance, weight, or driver rate
            Earning.objects.create(
                driver=instance.driver,
                shipment=instance,
                amount=50.00,  # Example fixed amount
                tenant=instance.tenant
            )
