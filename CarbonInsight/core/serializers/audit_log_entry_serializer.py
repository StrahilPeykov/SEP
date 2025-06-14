from auditlog.registry import auditlog
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType

class AuditLogEntrySerializer(serializers.ModelSerializer):
    """
    Serializes a django-auditlog LogEntry.
    - `actor` is the user who made the change.
    - `content_type` shows which model was changed.
    - `object_pk` is the primary key of the instance that was changed.

    Read-only fields:
            id
            timestamp
            actor_username
            content_type_app_label
            content_type_model
            object_pk
            action
            changes
    """
    actor_username = serializers.CharField(
        source="actor.username",
        read_only=True,
        default=None
    )
    content_type_app_label = serializers.ChoiceField(
        source="content_type.app_label",
        read_only=True,
        choices=[a._meta.app_label for a in auditlog.get_models()]
    )
    content_type_model = serializers.ChoiceField(
        source="content_type.model",
        read_only=True,
        choices=[m._meta.model_name for m in auditlog.get_models()]
    )
    changes = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "timestamp",
            "actor_username",
            "content_type_app_label",
            "content_type_model",
            "object_pk",
            "action",
            "changes",
        ]
        read_only_fields = fields

    def get_changes(self, obj: LogEntry) -> str:
        """
        Return changes in log entry.

        Returns:
            str: changes in log entry
        """
        return obj.changes_text if obj.changes_text else obj.changes_str


