from typing import Optional

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from core.models import Product
from core.models.product import ProductEmissionOverrideFactor
from rest_framework.validators import UniqueTogetherValidator


class ProductEmissionOverrideFactorSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductEmissionOverrideFactor.
    """
    # allow DRF-Writable-Nested to match existing records on update
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductEmissionOverrideFactor
        fields = ("id", "lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")

class ProductSerializer(WritableNestedModelSerializer):
    """
    Serializer for Product.
    """
    supplier = serializers.PrimaryKeyRelatedField(read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
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

    def _can_see_emissions(self, obj: Product) -> bool:
        u = self.context['request'].user
        sup = obj.supplier
        return (
                self.context.get('bypass_emission_permission_checks', False)
                or sup.user_is_member(u)
                or sup.auto_approve_product_sharing_requests
        )

    def get_emission_total(self, obj: Product) -> Optional[float]:
        """
        Returns the emission total for this product.

        Args:
            obj: Product object.
        Returns:
            total emission of the Product
        """

        if not self._can_see_emissions(obj):
            return None
        return obj.get_emission_trace().total

    def get_emission_total_non_biogenic(self, obj: Product) -> Optional[float]:
        """
        Returns the non-biogenic emission total for this product.

        Args:
            obj: Product object.
        Returns:
            total non-biogenic emission of the Product
        """

        if not self._can_see_emissions(obj):
            return None
        return obj.get_emission_trace().total_non_biogenic

    def get_emission_total_biogenic(self, obj: Product) -> Optional[float]:
        """
        Returns the biogenic emission total for this product.

        Args:
            obj: Product object.
        Returns:
            total biogenic emission of the Product
        """

        if not self._can_see_emissions(obj):
            return None
        return obj.get_emission_trace().total_biogenic

    def to_internal_value(self, data):
        """
        Adds parent Company to ProductBoMLineItemSerializer.

        Args:
            data: ProductBoMLineItemSerializer data
        Returns:
            modified ProductBoMLineItemSerializer data
        """

        # first perform the normal deserialization
        validated = super().to_internal_value(data)
        # now inject supplier from the URL
        validated["supplier"] = self.context["view"].get_parent_company()
        return validated