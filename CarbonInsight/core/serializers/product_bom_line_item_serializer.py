from typing import Union, Literal, Optional

from django.urls import reverse
from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import serializers
from core.models import ProductBoMLineItem, ProductSharingRequestStatus, Product, Emission, TransportEmission, \
    UserEnergyEmission, ProductionEnergyEmission
from core.serializers.product_serializer import ProductSerializer

class EmissionBoMSerializer(serializers.ModelSerializer):
    """
    Serializer for Emission.

    Read-only fields:
        quantity
    """

    type = serializers.SerializerMethodField(label="Emission type")
    url = serializers.SerializerMethodField(label="Link to detailed emission information API endpoint")

    class Meta:
        model = Emission
        fields = ("id", "quantity", "type", "url")
        read_only_fields = ("quantity",)

    @extend_schema_field(Literal["TransportEmission", "MaterialEmission",
                                 "UserEnergyEmission", "ProductionEnergyEmission"])
    def get_type(self, obj:Emission) -> str:
        """
        Gets the type of emission.

        Returns:
            Emission type
        """
        return obj.get_real_instance_class().__name__

    @extend_schema_field(serializers.URLField(allow_blank=False, allow_null=True))
    def get_url(self, obj:Emission) -> Optional[str]:
        """
        Returns the correct URL of the api for the emission.

        Args:
            obj: Emission object
        Returns:
            URL
        """

        company_pk = self.context['view'].kwargs['company_pk']
        product_pk = self.context['view'].kwargs['product_pk']
        if not company_pk or not product_pk:
            return None
        kwargs = {"company_pk": company_pk, "product_pk": product_pk, "pk": obj.id}
        if obj.get_real_instance_class() == TransportEmission:
            return reverse("product-transport-emissions-detail", kwargs=kwargs)
        elif obj.get_real_instance_class() == UserEnergyEmission:
            return reverse("product-user-energy-emissions-detail", kwargs=kwargs)
        elif obj.get_real_instance_class() == ProductionEnergyEmission:
            return reverse("product-production-energy-emissions-detail", kwargs=kwargs)
        return None


class ProductBoMLineItemSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductBoMLineItem.

    Read-only fields:
        parent_product
        line_item_product
        line_item_product_id
    """

    product_sharing_request_status = serializers.SerializerMethodField()
    line_item_product = ProductSerializer(read_only=True)
    emissions = EmissionBoMSerializer(many=True, read_only=True)
    # write-only id for creates/updates
    line_item_product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='line_item_product',
        write_only=True,
        required=False
    )

    class Meta:
        model = ProductBoMLineItem
        fields = ("id", "quantity", "line_item_product", "line_item_product_id", "parent_product", "product_sharing_request_status", "emissions")
        read_only_fields = ("parent_product", "line_item_product", "line_item_product_id")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ProductBoMLineItem.objects.all(),
                fields=["parent_product", "line_item_product"],
                message="A BoM line item with this product already exists in the parent product's BoM."
            )
        ]

    def get_product_sharing_request_status(self, obj:ProductBoMLineItem) -> ProductSharingRequestStatus:
        """
        returns the product sharing request status.

        Args:
            obj: ProductBoMLineItem object
        Returns:
            ProductSharingRequestStatus
        """
        return obj.product_sharing_request_status

    def to_internal_value(self, data):
        """
        Adds parent product to ProductBoMLineItemSerializer.

        Args:
            data: ProductBoMLineItemSerializer data
        Returns:
            modified ProductBoMLineItemSerializer data
        """

        # first perform the normal deserialization
        validated = super().to_internal_value(data)
        # now inject product from the URL
        validated["parent_product"] = self.context["view"].get_parent_product()
        return validated

    def create(self, validated_data):
        """
        Creates an BoMLineItem object from validated ProductBoMLineItemSerializer data.

        Args:
            validated_data: validated ProductBoMLineItemSerializer data
        Raises:
            ValidationError
        """

        if 'line_item_product' not in validated_data:
            raise serializers.ValidationError({"line_item_product_id": "This field is required for creation."})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Updates an BoMLineItem object with validated ProductBoMLineItemSerializer data.

        Args:
            instance: ProductBoMLineItemSerializer data extracted from a BoMLineItem object
            validated_data: validated ProductBoMLineItemSerializer data
        Raises:
            ValidationError
        """

        if 'line_item_product' in validated_data:
            raise serializers.ValidationError({"line_item_product_id": "This field cannot be updated after creation."})
        return super().update(instance, validated_data)

    def to_representation(self, instance: ProductBoMLineItem) -> dict:
        """
        Every time DRF is about to render this line-item,
        set the nested ProductSerializer’s bypass flag
        according to the sharing status.

        Args:
            instance: ProductBoMLineItem instance
        Returns:
            Serialized representation of the instance
        """
        accepted = (
            instance.product_sharing_request_status
            == ProductSharingRequestStatus.ACCEPTED
        )
        # flip its bypass_emission_permission_checks attribute
        self.context['bypass_emission_permission_checks'] = accepted
        # and let DRF do the rest
        return super().to_representation(instance)