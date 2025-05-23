from rest_framework import serializers

from core.models import (UserEnergyEmissionReference, ProductionEnergyEmissionReference,
                         MaterialEmissionReference, TransportEmissionReference)
from core.models.lifecycle_stage import LifecycleStage

class TransportEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = serializers.SerializerMethodField()

    class Meta:
        model = TransportEmissionReference
        fields = ("id", "name", "emission_factors")

    def get_emission_factors(self, obj: TransportEmissionReference) -> dict[LifecycleStage, float]:
        return {
            factor.lifecycle_stage: factor.co_2_emission_factor
            for factor in obj.reference_factors.all()
        }

class UserEnergyEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = serializers.SerializerMethodField()

    class Meta:
        model = UserEnergyEmissionReference
        fields = ("id", "name", "emission_factors")

    def get_emission_factors(self, obj: UserEnergyEmissionReference) -> dict[LifecycleStage, float]:
        return {
            factor.lifecycle_stage: factor.co_2_emission_factor
            for factor in obj.reference_factors.all()
        }

class ProductionEnergyEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = serializers.SerializerMethodField()

    class Meta:
        model = ProductionEnergyEmissionReference
        fields = ("id", "name", "emission_factors")

    def get_emission_factors(self, obj: ProductionEnergyEmissionReference) -> dict[LifecycleStage, float]:
        return {
            factor.lifecycle_stage: factor.co_2_emission_factor
            for factor in obj.reference_factors.all()
        }

class MaterialEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = serializers.SerializerMethodField()

    class Meta:
        model = MaterialEmissionReference
        fields = ("id", "name", "emission_factors")

    def get_emission_factors(self, obj: MaterialEmissionReference) -> dict[LifecycleStage, float]:
        return {
            factor.lifecycle_stage: factor.co_2_emission_factor
            for factor in obj.reference_factors.all()
        }