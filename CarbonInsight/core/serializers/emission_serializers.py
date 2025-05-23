from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from core.models import TransportEmission, EmissionOverrideFactor, MaterialEmission, UserEnergyEmission, \
    ProductionEnergyEmission

class EmissionOverrideFactorSerializer(serializers.ModelSerializer):
    # allow DRF-Writable-Nested to match existing records on update
    id = serializers.IntegerField(required=False)

    class Meta:
        model = EmissionOverrideFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor")

class TransportEmissionSerializer(WritableNestedModelSerializer):
    override_factors = EmissionOverrideFactorSerializer(many=True)

    class Meta:
        model = TransportEmission
        fields = ("id", "distance", "weight", "reference", "override_factors", "line_items")

class MaterialEmissionSerializer(WritableNestedModelSerializer):
    override_factors = EmissionOverrideFactorSerializer(many=True)

    class Meta:
        model = MaterialEmission
        fields = ("id", "weight", "reference", "override_factors", "line_items")

class UserEnergyEmissionSerializer(WritableNestedModelSerializer):
    override_factors = EmissionOverrideFactorSerializer(many=True)

    class Meta:
        model = UserEnergyEmission
        fields = ("id", "energy_consumption", "reference", "override_factors", "line_items")

class ProductionEnergyEmissionSerializer(WritableNestedModelSerializer):
    override_factors = EmissionOverrideFactorSerializer(many=True)

    class Meta:
        model = ProductionEnergyEmission
        fields = ("id", "energy_consumption", "reference", "override_factors", "line_items")