from typing import Union, Literal, Optional

from rest_framework import serializers
from core.models import ProductBoMLineItem, ProductSharingRequestStatus, Product
from core.serializers import ProductSerializer


class ProductBoMLineItemSerializer(serializers.ModelSerializer):
    product_sharing_request_status = serializers.SerializerMethodField()
    line_item_product = ProductSerializer(read_only=True)
    # write-only id for creates/updates
    line_item_product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='line_item_product',
        write_only=True
    )

    class Meta:
        model = ProductBoMLineItem
        fields = ("id", "quantity", "line_item_product", "line_item_product_id", "parent_product", "product_sharing_request_status")
        read_only_fields = ("parent_product", "line_item_product")

    def get_product_sharing_request_status(self, obj:ProductBoMLineItem) -> Union[ProductSharingRequestStatus, Literal["Not requested"]]:
        product_sharing_request= obj.product_sharing_request
        if product_sharing_request is not None:
            return product_sharing_request.status
        return "Not requested"
