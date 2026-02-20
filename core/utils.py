import os
import json


def create_audit_log(user, action, entity_type, entity_id, changes=None, tenant=None):
    """Helper to create an audit log entry."""
    from auditlogs.models import AuditLog
    AuditLog.objects.create(
        user=user,
        tenant=tenant,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        changes=changes or {},
    )


def upload_to(instance, filename):
    """Generate upload path based on model name and instance ID."""
    model_name = instance.__class__.__name__.lower()
    return os.path.join('uploads', model_name, str(instance.id), filename)


def kyc_upload_path(instance, filename):
    return os.path.join('uploads', 'kyc', str(instance.driver_id), filename)


def proof_upload_path(instance, filename):
    return os.path.join('uploads', 'delivery_proof', str(instance.shipment_id), filename)
