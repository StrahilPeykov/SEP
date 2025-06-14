from typing import Optional

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from core.models.emission_trace import EmissionTrace, EmissionTraceChild

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from core.models.emission_trace import EmissionTrace, EmissionTraceChild


class EmissionTraceChildSerializer(DataclassSerializer):
    """
    Serializer for EmissionTraceChild.
    """

    quantity = serializers.FloatField()
    # we use SerializerMethodField here so we can import the parent serializer lazily
    emission_trace = serializers.SerializerMethodField()

    class Meta:
        dataclass = EmissionTraceChild
        fields = ("quantity", "emission_trace")

    def get_emission_trace(self, obj: EmissionTraceChild) -> dict:
        """
        Returns the EmissionTrace objects contents as simple datatypes of Python.

        Returns:
            emission trace
        """

        return EmissionTraceSerializer(obj.emission_trace).data


class EmissionTraceSerializer(DataclassSerializer):
    """
    Serializer for EmissionTrace.
    """

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
        """
        Returns the total emission of emission trace.

        Returns:
            total emission of everything returned in emission trace
        """
        return obj.total

    def get_source(self, obj: EmissionTrace) -> Optional[str]:
        """
        Returns the source of the emission trace.

        Returns:
            source of the emission trace
        """
        return obj.source
