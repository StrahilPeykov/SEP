from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from core.models import TransportEmission, EmissionOverrideFactor, MaterialEmission, UserEnergyEmission, \
    ProductionEnergyEmission, ProductBoMLineItem, TransportEmissionReference, MaterialEmissionReference, \
    UserEnergyEmissionReference, ProductionEnergyEmissionReference
from core.serializers.reference_serializers import ProductionEnergyEmissionReferenceSerializer, \
    TransportEmissionReferenceSerializer, UserEnergyEmissionReferenceSerializer, MaterialEmissionReferenceSerializer


class EmissionOverrideFactorSerializer(serializers.ModelSerializer):
    # allow DRF-Writable-Nested to match existing records on update
    id = serializers.IntegerField(required=False)

    class Meta:
        model = EmissionOverrideFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class TransportEmissionSerializer(WritableNestedModelSerializer):
    override_factors = EmissionOverrideFactorSerializer(many=True, required=False)
    line_items = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductBoMLineItem.objects.all(),
        required=False,     # Not required on create/update
        default=list        # If omitted, validated_data.get('line_items') = []
    )
    reference_details = TransportEmissionReferenceSerializer(read_only=True, source="reference")

    class Meta:
        model = TransportEmission
        fields = ("id", "distance", "weight", "reference", "reference_details", "override_factors", "line_items")

class MaterialEmissionSerializer(WritableNestedModelSerializer):
    override_factors = EmissionOverrideFactorSerializer(many=True, required=False)
    line_items = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductBoMLineItem.objects.all(),
        required=False,     # Not required on create/update
        default=list        # If omitted, validated_data.get('line_items') = []
    )
    reference_details = MaterialEmissionReferenceSerializer(read_only=True, source="reference")

    class Meta:
        model = MaterialEmission
        fields = ("id", "weight", "reference", "reference_details", "override_factors", "line_items")

class UserEnergyEmissionSerializer(WritableNestedModelSerializer):
    override_factors = EmissionOverrideFactorSerializer(many=True, required=False)
    line_items = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductBoMLineItem.objects.all(),
        required=False,     # Not required on create/update
        default=list        # If omitted, validated_data.get('line_items') = []
    )
    reference_details = UserEnergyEmissionReferenceSerializer(read_only=True, source="reference")

    class Meta:
        model = UserEnergyEmission
        fields = ("id", "energy_consumption", "reference", "reference_details", "override_factors", "line_items")

class ProductionEnergyEmissionSerializer(WritableNestedModelSerializer):
    override_factors = EmissionOverrideFactorSerializer(many=True, required=False)
    line_items = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductBoMLineItem.objects.all(),
        required=False,     # Not required on create/update
        default=list        # If omitted, validated_data.get('line_items') = []
    )
    reference_details = ProductionEnergyEmissionReferenceSerializer(read_only=True, source="reference")

    class Meta:
        model = ProductionEnergyEmission
        fields = ("id", "energy_consumption", "reference", "reference_details", "override_factors", "line_items")