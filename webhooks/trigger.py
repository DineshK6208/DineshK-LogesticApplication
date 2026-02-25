"""
webhooks/trigger.py
───────────────────
Outbound webhook dispatcher.

When an internal event occurs (shipment status change, payment update,
payout processed), this module:

1. Finds all active WebhookEndpoints subscribed to that event.
2. Sends an HMAC-signed POST request to each endpoint URL.
3. Logs the attempt in WebhookLog (success or failure).
4. Supports automatic retry for failed deliveries.
"""

import hashlib
import hmac
import json
import logging
import uuid
from datetime import timedelta

import requests
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from .models import WebhookEndpoint, WebhookLog

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────
WEBHOOK_TIMEOUT = getattr(settings, 'WEBHOOK_TIMEOUT', 10)          # seconds
WEBHOOK_MAX_RETRIES = getattr(settings, 'WEBHOOK_MAX_RETRIES', 3)
WEBHOOK_RETRY_DELAYS = [60, 300, 900]  # seconds: 1min, 5min, 15min


# ──────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────

def trigger_webhook(event: str, payload: dict, tenant=None) -> list:
    """
    Fire an outbound webhook for the given event.

    Args:
        event:   Event name, e.g. 'shipment.status_changed'
        payload: Dict to send as JSON body
        tenant:  Optional tenant to scope the endpoints

    Returns:
        List of WebhookLog instances created.
    """
    endpoints = WebhookEndpoint.objects.filter(is_active=True)

    if tenant:
        endpoints = endpoints.filter(tenant=tenant)

    # Filter endpoints that subscribe to this event
    matching = [ep for ep in endpoints if event in (ep.events or [])]

    if not matching:
        logger.debug("No endpoints registered for event=%s", event)
        return []

    logs = []
    for endpoint in matching:
        log = _deliver(endpoint, event, payload)
        logs.append(log)

    return logs


def retry_failed_webhooks() -> int:
    """
    Retry all failed webhook deliveries that are eligible.

    Call this from a management command, cron job, or Celery beat.

    Returns:
        Number of webhooks retried.
    """
    now = timezone.now()
    failed_logs = WebhookLog.objects.filter(
        delivery_status=WebhookLog.DeliveryStatus.FAILED,
        next_retry_at__lte=now,
        attempts__lt=F('max_retries'),
    ).select_related('endpoint')

    retried = 0
    for log in failed_logs:
        if not log.endpoint.is_active:
            continue
        _retry_delivery(log)
        retried += 1

    logger.info("Retried %d failed webhooks", retried)
    return retried


# ──────────────────────────────────────────────
#  Internal helpers
# ──────────────────────────────────────────────

def _sign_payload(secret: str, payload_bytes: bytes) -> str:
    """Generate HMAC-SHA256 signature."""
    if not secret:
        return ''
    return hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()


def _deliver(endpoint: WebhookEndpoint, event: str, payload: dict) -> WebhookLog:
    """
    Send a single webhook and create a WebhookLog entry.
    """
    payload_with_meta = {
        'webhook_id': str(uuid.uuid4()),
        'event': event,
        'timestamp': timezone.now().isoformat(),
        'data': payload,
    }
    body = json.dumps(payload_with_meta, default=str)
    signature = _sign_payload(endpoint.secret, body.encode())

    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Signature': signature,
        'X-Webhook-Event': event,
    }

    log = WebhookLog(
        endpoint=endpoint,
        tenant=endpoint.tenant,
        event=event,
        payload=payload_with_meta,
        attempts=1,
        max_retries=WEBHOOK_MAX_RETRIES,
    )

    try:
        response = requests.post(
            endpoint.url,
            data=body,
            headers=headers,
            timeout=WEBHOOK_TIMEOUT,
        )
        log.status_code = response.status_code

        if 200 <= response.status_code < 300:
            log.delivery_status = WebhookLog.DeliveryStatus.SUCCESS
            logger.info(
                "Webhook delivered: event=%s url=%s status=%d",
                event, endpoint.url, response.status_code,
            )
        else:
            log.delivery_status = WebhookLog.DeliveryStatus.FAILED
            log.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
            log.next_retry_at = timezone.now() + timedelta(seconds=WEBHOOK_RETRY_DELAYS[0])
            logger.warning(
                "Webhook failed: event=%s url=%s status=%d",
                event, endpoint.url, response.status_code,
            )

    except requests.RequestException as exc:
        log.delivery_status = WebhookLog.DeliveryStatus.FAILED
        log.error_message = str(exc)[:500]
        log.next_retry_at = timezone.now() + timedelta(seconds=WEBHOOK_RETRY_DELAYS[0])
        logger.exception("Webhook request error: event=%s url=%s", event, endpoint.url)

    log.save()
    return log


def _retry_delivery(log: WebhookLog) -> None:
    """
    Retry a previously failed webhook delivery.
    """
    body = json.dumps(log.payload, default=str)
    signature = _sign_payload(log.endpoint.secret, body.encode())

    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Signature': signature,
        'X-Webhook-Event': log.event,
    }

    log.attempts += 1

    try:
        response = requests.post(
            log.endpoint.url,
            data=body,
            headers=headers,
            timeout=WEBHOOK_TIMEOUT,
        )
        log.status_code = response.status_code

        if 200 <= response.status_code < 300:
            log.delivery_status = WebhookLog.DeliveryStatus.SUCCESS
            log.next_retry_at = None
            logger.info(
                "Webhook retry succeeded: log=%s attempt=%d",
                log.id, log.attempts,
            )
        else:
            log.delivery_status = WebhookLog.DeliveryStatus.FAILED
            log.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
            _schedule_next_retry(log)

    except requests.RequestException as exc:
        log.delivery_status = WebhookLog.DeliveryStatus.FAILED
        log.error_message = str(exc)[:500]
        _schedule_next_retry(log)
        logger.exception("Webhook retry failed: log=%s attempt=%d", log.id, log.attempts)

    log.save()


def _schedule_next_retry(log: WebhookLog) -> None:
    """Calculate the next retry time based on attempt count."""
    attempt_index = min(log.attempts - 1, len(WEBHOOK_RETRY_DELAYS) - 1)
    delay = WEBHOOK_RETRY_DELAYS[attempt_index]
    log.next_retry_at = timezone.now() + timedelta(seconds=delay)
    logger.info(
        "Next retry for log=%s scheduled in %ds (attempt %d/%d)",
        log.id, delay, log.attempts, log.max_retries,
    )
