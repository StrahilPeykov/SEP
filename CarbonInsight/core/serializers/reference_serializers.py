from rest_framework import serializers

from core.models import (UserEnergyEmissionReference, ProductionEnergyEmissionReference,
                         TransportEmissionReference,
                         ProductionEnergyEmissionReferenceFactor, UserEnergyEmissionReferenceFactor,
                         TransportEmissionReferenceFactor)
from core.models.lifecycle_stage import LifecycleStage

class TransportEmissionReferenceFactorSerializer(serializers.ModelSerializer):
    """
    Serializer for TransportEmissionReferenceFactor.
    """

    class Meta:
        model = TransportEmissionReferenceFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class TransportEmissionReferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for TransportEmissionReference.
    """

    emission_factors = TransportEmissionReferenceFactorSerializer(many=True, source="reference_factors")

    class Meta:
        model = TransportEmissionReference
        fields = ("id", "name", "emission_factors")

class UserEnergyEmissionReferenceFactorSerializer(serializers.ModelSerializer):
    """
    Serializer for UserEnergyEmissionReferenceFactor.
    """

    class Meta:
        model = UserEnergyEmissionReferenceFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class UserEnergyEmissionReferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for UserEnergyEmissionReference.
    """

    emission_factors = UserEnergyEmissionReferenceFactorSerializer(many=True, source="reference_factors")

    class Meta:
        model = UserEnergyEmissionReference
        fields = ("id", "name", "emission_factors")

class ProductionEnergyEmissionReferenceFactorSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductionEnergyEmissionReferenceFactor.
    """

    class Meta:
        model = ProductionEnergyEmissionReferenceFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class ProductionEnergyEmissionReferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductionEnergyEmissionReference.
    """

    emission_factors = ProductionEnergyEmissionReferenceFactorSerializer(many=True, source="reference_factors")

    class Meta:
        model = ProductionEnergyEmissionReference
        fields = ("id", "name", "emission_factors")
