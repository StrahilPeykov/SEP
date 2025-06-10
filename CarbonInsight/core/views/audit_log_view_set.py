from auditlog.models import LogEntry
from auditlog.registry import auditlog
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.filters import AuditLogFilter
from core.serializers.audit_log_entry_serializer import AuditLogEntrySerializer

registered_models = auditlog.get_models()
registered_names = [
    f"{m._meta.app_label}.{m._meta.model_name}"
    for m in registered_models
]

@extend_schema_view(
    list=extend_schema(
        tags=["Audit log"],
        summary="Retrieve audit log entries",
        description="Retrieve a list of all audit log entries. "
                    "You can filter by content type and object primary key.",
        parameters=[
            OpenApiParameter(
                name="content_type",
                type=str,
                enum=registered_names,
                description="Filter by content type in the format 'app_label.model'.",
                required=False,
            ),
            OpenApiParameter(
                name="object_pk",
                type=int,
                description="Filter by the primary key of the object.",
                required=False,
            ),
        ]
    ),
    retrieve=extend_schema(
        tags=["Audit log"],
        summary="Retrieve a specific audit log entry",
        description="Retrieve a specific audit log entry by its ID.",
    ),
)
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogEntry.objects.all().order_by("-timestamp")
    serializer_class = AuditLogEntrySerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_class = AuditLogFilter