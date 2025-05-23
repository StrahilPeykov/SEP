from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from core.models import Product
from core.models.product import ProductEmissionOverrideFactor


class ProductEmissionOverrideFactorSerializer(serializers.ModelSerializer):
    # allow DRF-Writable-Nested to match existing records on update
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductEmissionOverrideFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor")

class ProductSerializer(WritableNestedModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(read_only=True)
    emission_total = serializers.SerializerMethodField()
    override_factors = ProductEmissionOverrideFactorSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = "__all__"

    def get_emission_total(self, obj: Product) -> float:
        return obj.get_emission_trace().total