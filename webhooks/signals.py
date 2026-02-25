"""
webhooks/signals.py
───────────────────
Django signals that automatically trigger outbound webhooks
when internal models change:

- Shipment status change  → event: shipment.status_changed
- Payment update          → event: payment.updated
- Payout processed        → event: payout.processed
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
#  Shipment status change
# ──────────────────────────────────────────────

@receiver(pre_save, sender='shipments.Shipment')
def capture_old_shipment_status(sender, instance, **kwargs):
    """Store the old status before saving so we can detect changes."""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender='shipments.Shipment')
def trigger_shipment_webhook(sender, instance, created, **kwargs):
    """Fire webhook when shipment status changes."""
    from .trigger import trigger_webhook

    old_status = getattr(instance, '_old_status', None)

    # Trigger on new shipment OR status change
    if created or (old_status and old_status != instance.status):
        event = 'shipment.status_changed'
        payload = {
            'shipment_id': str(instance.id),
            'tracking_number': instance.tracking_number,
            'old_status': old_status or 'new',
            'new_status': instance.status,
            'receiver_name': instance.receiver_name,
            'receiver_address': instance.receiver_address,
        }

        tenant = instance.tenant if hasattr(instance, 'tenant') else None
        trigger_webhook(event, payload, tenant=tenant)

        logger.info(
            "Shipment webhook triggered: %s → %s (tracking=%s)",
            old_status, instance.status, instance.tracking_number,
        )


# ──────────────────────────────────────────────
#  Payment update
# ──────────────────────────────────────────────

@receiver(pre_save, sender='payments.Payment')
def capture_old_payment_status(sender, instance, **kwargs):
    """Store the old status before saving so we can detect changes."""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender='payments.Payment')
def trigger_payment_webhook(sender, instance, created, **kwargs):
    """Fire webhook when payment status changes."""
    from .trigger import trigger_webhook

    old_status = getattr(instance, '_old_status', None)

    if created or (old_status and old_status != instance.status):
        event = 'payment.updated'
        payload = {
            'payment_id': str(instance.id),
            'tracking_number': instance.shipment.tracking_number,
            'amount': str(instance.amount),
            'mode': instance.mode,
            'old_status': old_status or 'new',
            'new_status': instance.status,
            'transaction_id': instance.transaction_id,
        }

        tenant = instance.tenant if hasattr(instance, 'tenant') else None
        trigger_webhook(event, payload, tenant=tenant)

        logger.info(
            "Payment webhook triggered: %s → %s (payment=%s)",
            old_status, instance.status, instance.id,
        )


# ──────────────────────────────────────────────
#  Payout processed
# ──────────────────────────────────────────────

@receiver(pre_save, sender='earnings.Payout')
def capture_old_payout_status(sender, instance, **kwargs):
    """Store the old status before saving so we can detect changes."""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender='earnings.Payout')
def trigger_payout_webhook(sender, instance, created, **kwargs):
    """Fire webhook when payout status changes."""
    from .trigger import trigger_webhook

    old_status = getattr(instance, '_old_status', None)

    if created or (old_status and old_status != instance.status):
        event = 'payout.processed'
        payload = {
            'payout_id': str(instance.id),
            'driver_id': str(instance.driver.id),
            'amount': str(instance.amount),
            'old_status': old_status or 'new',
            'new_status': instance.status,
        }

        tenant = instance.tenant if hasattr(instance, 'tenant') else None
        trigger_webhook(event, payload, tenant=tenant)

        logger.info(
            "Payout webhook triggered: %s → %s (payout=%s)",
            old_status, instance.status, instance.id,
        )
