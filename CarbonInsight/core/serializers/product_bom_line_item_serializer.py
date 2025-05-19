from typing import Union, Literal, Optional

from django.urls import reverse
from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import serializers
from core.models import ProductBoMLineItem, ProductSharingRequestStatus, Product, Emission, TransportEmission, \
    MaterialEmission, UserEnergyEmission, ProductionEnergyEmission
from core.serializers import ProductSerializer

class EmissionBoMSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(label="Emission type")
    url = serializers.SerializerMethodField(label="Link to detailed emission information API endpoint")

    class Meta:
        model = Emission
        fields = ("id", "quantity", "type", "url")
        read_only_fields = ("quantity",)

    @extend_schema_field(Literal["TransportEmission", "MaterialEmission",
                                 "UserEnergyEmission", "ProductionEnergyEmission"])
    def get_type(self, obj:Emission) -> str:
        return obj.get_real_instance_class().__name__

    @extend_schema_field(serializers.URLField(allow_blank=False, allow_null=True))
    def get_url(self, obj:Emission) -> Optional[str]:
        company_pk = self.context['view'].kwargs['company_pk']
        product_pk = self.context['view'].kwargs['product_pk']
        if not company_pk or not product_pk:
            return None
        kwargs = {"company_pk": company_pk, "product_pk": product_pk, "pk": obj.id}
        if obj.get_real_instance_class() == TransportEmission:
            return reverse("product-transport-emissions-detail", kwargs=kwargs)
        elif obj.get_real_instance_class() == MaterialEmission:
            return reverse("product-material-emissions-detail", kwargs=kwargs)
        elif obj.get_real_instance_class() == UserEnergyEmission:
            return reverse("product-user-energy-emissions-detail", kwargs=kwargs)
        elif obj.get_real_instance_class() == ProductionEnergyEmission:
            return reverse("product-production-energy-emissions-detail", kwargs=kwargs)
        return None


class ProductBoMLineItemSerializer(serializers.ModelSerializer):
    product_sharing_request_status = serializers.SerializerMethodField()
    line_item_product = ProductSerializer(read_only=True)
    emissions = EmissionBoMSerializer(many=True, read_only=True)
    # write-only id for creates/updates
    line_item_product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='line_item_product',
        write_only=True
    )

    class Meta:
        model = ProductBoMLineItem
        fields = ("id", "quantity", "line_item_product", "line_item_product_id", "parent_product", "product_sharing_request_status", "emissions")
        read_only_fields = ("parent_product", "line_item_product")

    @extend_schema_field({
        'type': 'string',
        'enum': ['Not requested'] + [c.value for c in ProductSharingRequestStatus]
    })
    def get_product_sharing_request_status(self, obj:ProductBoMLineItem) -> str:
        product_sharing_request = obj.product_sharing_request
        if product_sharing_request is None:
            return "Not requested"
        return ProductSharingRequestStatus(product_sharing_request.status)
