from rest_framework import serializers
from core.models import ProductSharingRequest

class ProductSharingRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductSharingRequest.
    """
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductSharingRequest
        fields = "__all__"

class ProductSharingRequestRequestAccessSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductSharingRequestRequestAccess.
    """
    class Meta:
        model = ProductSharingRequest
        fields = ["requester"]