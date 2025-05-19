from rest_framework.generics import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Product, ProductBoMLineItem, Company
from core.permissions import ProductSubAPIPermission
from core.serializers.product_bom_line_item_serializer import ProductBoMLineItemSerializer
from core.views.mixins.company_mixin import CompanyMixin
from core.views.mixins.product_mixin import ProductMixin


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="company_pk",
            type=int,
            location="path",
            description="Primary key of the parent Company",
        ),
        OpenApiParameter(
            name="product_pk",
            type=int,
            location="path",
            description="Primary key of the parent Product",
        ),
        OpenApiParameter(
            name="id",
            type=int,
            location="path",
            description="Primary key of the BoM line item",
        )
    ],
)
@extend_schema_view(
    list=extend_schema(
        tags=["Product BoM line items"],
        summary="Retrieve all BoM line items for a product",
        description="Retrieve all BoM line items for a specific product. "
    ),
    retrieve=extend_schema(
        tags=["Product BoM line items"],
        summary="Retrieve a specific BoM line item for a product",
        description="Retrieve a specific BoM line item for a product. "
    ),
    create=extend_schema(
        tags=["Product BoM line items"],
        summary="Create a new BoM line item for a product",
        description="Create a new BoM line item for a specific product. "
    ),
    update=extend_schema(
        tags=["Product BoM line items"],
        summary="Update a BoM line item for a product",
        description="Update a specific BoM line item for a product. "
    ),
    partial_update=extend_schema(
        tags=["Product BoM line items"],
        summary="Partially update a BoM line item for a product",
        description="Partially update a specific BoM line item for a product. "
    ),
    destroy=extend_schema(
        tags=["Product BoM line items"],
        summary="Delete a BoM line item for a product",
        description="Delete a specific BoM line item for a product. "
    ),
)
class ProductBoMLineItemViewSet(
    CompanyMixin,
    ProductMixin,
    viewsets.ModelViewSet
):
    queryset = ProductBoMLineItem.objects.none()  # Set to none to force overriding get_queryset
    serializer_class = ProductBoMLineItemSerializer
    permission_classes = [IsAuthenticated, ProductSubAPIPermission]

    def get_queryset(self):
        product = self.get_parent_product()
        qs = ProductBoMLineItem.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        product = self.get_parent_product()
        serializer.save(parent_product=product)