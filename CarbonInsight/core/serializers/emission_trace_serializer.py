from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from core.models.emission_trace import EmissionTrace


class EmissionTraceSerializer(DataclassSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        dataclass = EmissionTrace

    def get_total(self, obj: EmissionTrace) -> float:
        return obj.total