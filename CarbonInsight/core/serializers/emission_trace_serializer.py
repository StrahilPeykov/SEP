from typing import Optional

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from core.models.emission_trace import EmissionTrace, EmissionTraceChild

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from core.models.emission_trace import EmissionTrace, EmissionTraceChild


class EmissionTraceChildSerializer(DataclassSerializer):
    quantity = serializers.FloatField()
    # we use SerializerMethodField here so we can import the parent serializer lazily
    emission_trace = serializers.SerializerMethodField()

    class Meta:
        dataclass = EmissionTraceChild
        fields = ("quantity", "emission_trace")

    def get_emission_trace(self, obj: EmissionTraceChild) -> dict:
        return EmissionTraceSerializer(obj.emission_trace).data


class EmissionTraceSerializer(DataclassSerializer):
    total = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    # now that the child is defined above, we can reference it directly
    children = EmissionTraceChildSerializer(many=True)

    class Meta:
        dataclass = EmissionTrace
        fields = (
            "label",
            "reference_impact_unit",
            #"related_object",
            "methodology",
            "emissions_subtotal",
            "children",
            "mentions",
            "total",
            "pcf_calculation_method",
            "source",
        )

    def get_total(self, obj: EmissionTrace) -> float:
        return obj.total

    def get_source(self, obj: EmissionTrace) -> Optional[str]:
        return obj.source
