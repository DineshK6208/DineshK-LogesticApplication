from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'entity_type', 'entity_id', 'changes', 'timestamp']
        read_only_fields = ['id', 'timestamp']
