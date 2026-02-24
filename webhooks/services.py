"""
webhooks/services.py
────────────────────
Business-logic layer for processing incoming webhooks.

Each handler receives a ReceivedWebhook instance and performs the
domain-specific side-effects (updating Payment / Shipment tables).
"""

import logging
from django.utils import timezone

from .models import ReceivedWebhook

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Public dispatcher
# ──────────────────────────────────────────────

def process_webhook(webhook: ReceivedWebhook) -> None:
    """
    Route a received webhook to the correct handler based on its
    source and event_type.  Updates the webhook status to
    *processed* or *failed*.
    """
    handler_map = {
        # ── Payment events (Razorpay) ─────────────────
        'payment.success': _handle_payment_success,
        'payment.failed': _handle_payment_failed,

        # ── Shipment events (Shiprocket / Delhivery) ──
        'shipment.in_transit': _handle_shipment_in_transit,
        'shipment.out_for_delivery': _handle_shipment_out_for_delivery,
        'shipment.delivered': _handle_shipment_delivered,
        'shipment.rto': _handle_shipment_rto,
    }

    handler = handler_map.get(webhook.event_type)
    if handler is None:
        logger.warning(
            "No handler for event_type=%s (webhook id=%s)",
            webhook.event_type,
            webhook.id,
        )
        webhook.status = ReceivedWebhook.Status.FAILED
        webhook.error_detail = f"Unknown event_type: {webhook.event_type}"
        webhook.processed_at = timezone.now()
        webhook.save(update_fields=['status', 'error_detail', 'processed_at'])
        return

    try:
        handler(webhook)
        webhook.status = ReceivedWebhook.Status.PROCESSED
        webhook.processed_at = timezone.now()
        webhook.save(update_fields=['status', 'processed_at'])
        logger.info(
            "Webhook processed: id=%s event=%s",
            webhook.id,
            webhook.event_type,
        )
    except Exception as exc:
        logger.exception("Webhook processing failed: id=%s", webhook.id)
        webhook.status = ReceivedWebhook.Status.FAILED
        webhook.error_detail = str(exc)
        webhook.processed_at = timezone.now()
        webhook.save(update_fields=['status', 'error_detail', 'processed_at'])


# ──────────────────────────────────────────────
#  Payment handlers
# ──────────────────────────────────────────────

def _handle_payment_success(webhook: ReceivedWebhook) -> None:
    """Mark the related Payment as completed."""
    from payments.models import Payment          # avoid circular import

    payload = webhook.payload
    transaction_id = payload.get('transaction_id') or payload.get('razorpay_payment_id', '')
    shipment_tracking = payload.get('tracking_number', '')

    if not shipment_tracking:
        raise ValueError("payload missing 'tracking_number'")

    payment = Payment.objects.select_for_update().get(
        shipment__tracking_number=shipment_tracking,
    )
    payment.status = 'completed'
    payment.transaction_id = transaction_id
    payment.metadata = payload
    payment.save(update_fields=['status', 'transaction_id', 'metadata', 'updated_at'])

    logger.info(
        "Payment marked completed for shipment %s (txn=%s)",
        shipment_tracking,
        transaction_id,
    )


def _handle_payment_failed(webhook: ReceivedWebhook) -> None:
    """Mark the related Payment as failed."""
    from payments.models import Payment

    payload = webhook.payload
    shipment_tracking = payload.get('tracking_number', '')

    if not shipment_tracking:
        raise ValueError("payload missing 'tracking_number'")

    payment = Payment.objects.select_for_update().get(
        shipment__tracking_number=shipment_tracking,
    )
    payment.status = 'failed'
    payment.metadata = payload
    payment.save(update_fields=['status', 'metadata', 'updated_at'])

    logger.info("Payment marked failed for shipment %s", shipment_tracking)


# ──────────────────────────────────────────────
#  Shipment handlers
# ──────────────────────────────────────────────

def _update_shipment_status(webhook: ReceivedWebhook, new_status: str) -> None:
    """Generic helper to transition a shipment to *new_status*."""
    from shipments.models import Shipment

    payload = webhook.payload
    tracking_number = payload.get('tracking_number') or payload.get('awb', '')

    if not tracking_number:
        raise ValueError("payload missing 'tracking_number' or 'awb'")

    shipment = Shipment.objects.select_for_update().get(
        tracking_number=tracking_number,
    )
    shipment.status = new_status

    # If delivered → stamp delivered_at
    if new_status == 'delivered':
        shipment.delivered_at = timezone.now()

    shipment.save(update_fields=['status', 'delivered_at', 'updated_at'])

    logger.info(
        "Shipment %s → %s (webhook id=%s)",
        tracking_number,
        new_status,
        webhook.id,
    )


def _handle_shipment_in_transit(webhook: ReceivedWebhook) -> None:
    _update_shipment_status(webhook, 'in_transit')


def _handle_shipment_out_for_delivery(webhook: ReceivedWebhook) -> None:
    _update_shipment_status(webhook, 'out_for_delivery')


def _handle_shipment_delivered(webhook: ReceivedWebhook) -> None:
    _update_shipment_status(webhook, 'delivered')


def _handle_shipment_rto(webhook: ReceivedWebhook) -> None:
    _update_shipment_status(webhook, 'rto')
