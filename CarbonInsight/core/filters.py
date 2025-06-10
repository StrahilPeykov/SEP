import django_filters
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType


class AuditLogFilter(django_filters.FilterSet):
    # Allow filtering by "app_label.model" in a single param:
    content_type = django_filters.CharFilter(
        method="filter_by_content_type"
    )

    class Meta:
        model = LogEntry
        # We only declare the custom filters here; all other fields would be declared manually if needed.
        fields = ["content_type", "object_pk"]

    def filter_by_content_type(self, queryset, name, value):
        """
        value is expected to be "app_label.model" (e.g. "auth.user").
        """
        try:
            app_label, model_name = value.split(".")
        except ValueError:
            return queryset.none()

        ct = ContentType.objects.filter(
            app_label__iexact=app_label.strip(),
            model__iexact=model_name.strip()
        ).first()
        if not ct:
            return queryset.none()
        return queryset.filter(content_type=ct)