from rest_framework import serializers

from core.models import UserEnergyEmissionReference, ProductionEnergyEmissionReference, MaterialEmissionReference, \
    EndOfLifeEmissionReference
from core.models.lifecycle_stage import LifecycleStage
from core.models.transport_emission import TransportEmissionReference

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

class EndOfLifeEmissionReferenceSerializer(serializers.ModelSerializer):
    emission_factors = serializers.SerializerMethodField()

    class Meta:
        model = EndOfLifeEmissionReference
        fields = ("id", "name", "emission_factors", "landfill_percentage",
                  "incineration_percentage", "recycled_percentage", "reused_percentage")

    def get_emission_factors(self, obj: EndOfLifeEmissionReference) -> dict[LifecycleStage, float]:
        return {
            factor.lifecycle_stage: factor.co_2_emission_factor
            for factor in obj.reference_factors.all()
        }