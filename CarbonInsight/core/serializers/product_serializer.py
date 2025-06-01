from typing import Optional

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from core.models import Product
from core.models.product import ProductEmissionOverrideFactor
from rest_framework.validators import UniqueTogetherValidator


class ProductEmissionOverrideFactorSerializer(serializers.ModelSerializer):
    # allow DRF-Writable-Nested to match existing records on update
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductEmissionOverrideFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class ProductSerializer(WritableNestedModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(read_only=True)
    emission_total = serializers.SerializerMethodField()
    emission_total_non_biogenic = serializers.SerializerMethodField()
    emission_total_biogenic = serializers.SerializerMethodField()
    override_factors = ProductEmissionOverrideFactorSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Product.objects.all(),
                fields=["supplier", "name", "manufacturer_name", "sku"],
                message="A product with this supplier, name, manufacturer and SKU already exists."
            )
        ]

    def get_emission_total(self, obj: Product) -> Optional[float]:
        if not obj.supplier.user_is_member(self.context['request'].user):
            return None
        return obj.get_emission_trace().total

    def get_emission_total_non_biogenic(self, obj: Product) -> Optional[float]:
        if not obj.supplier.user_is_member(self.context['request'].user):
            return None
        return obj.get_emission_trace().total_non_biogenic

    def get_emission_total_biogenic(self, obj: Product) -> Optional[float]:
        if not obj.supplier.user_is_member(self.context['request'].user):
            return None
        return obj.get_emission_trace().total_biogenic

    def to_internal_value(self, data):
        # first perform the normal deserialization
        validated = super().to_internal_value(data)
        # now inject supplier from the URL
        validated["supplier"] = self.context["view"].get_parent_company()
        return validated