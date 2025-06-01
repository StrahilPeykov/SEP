from rest_framework import serializers

from core.models import (UserEnergyEmissionReference, ProductionEnergyEmissionReference,
                         MaterialEmissionReference, TransportEmissionReference, MaterialEmissionReferenceFactor,
                         ProductionEnergyEmissionReferenceFactor, UserEnergyEmissionReferenceFactor,
                         TransportEmissionReferenceFactor)
from core.models.lifecycle_stage import LifecycleStage

class TransportEmissionReferenceFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportEmissionReferenceFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class TransportEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = TransportEmissionReferenceFactorSerializer(many=True, source="reference_factors")

    class Meta:
        model = TransportEmissionReference
        fields = ("id", "name", "emission_factors")

class UserEnergyEmissionReferenceFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEnergyEmissionReferenceFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class UserEnergyEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = UserEnergyEmissionReferenceFactorSerializer(many=True, source="reference_factors")

    class Meta:
        model = UserEnergyEmissionReference
        fields = ("id", "name", "emission_factors")

class ProductionEnergyEmissionReferenceFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionEnergyEmissionReferenceFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class ProductionEnergyEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = ProductionEnergyEmissionReferenceFactorSerializer(many=True, source="reference_factors")

    class Meta:
        model = ProductionEnergyEmissionReference
        fields = ("id", "name", "emission_factors")

class MaterialEmissionReferenceFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialEmissionReferenceFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class MaterialEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = MaterialEmissionReferenceFactorSerializer(many=True, source="reference_factors")

    class Meta:
        model = MaterialEmissionReference
        fields = ("id", "name", "emission_factors")