from rest_framework.generics import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Product, ProductBoMLineItem, Company
from core.permissions import ProductBoMLineItemPermission
from core.serializers.product_bom_line_item_serializer import ProductBoMLineItemSerializer


class ProductBoMLineItemViewSet(viewsets.ModelViewSet):
    serializer_class = ProductBoMLineItemSerializer
    permission_classes = [IsAuthenticated, ProductBoMLineItemPermission]

    def get_parent_company(self):
        # drf-nested-routers stores the company pk in kwargs
        return get_object_or_404(Company, pk=self.kwargs['company_pk'])

    def get_parent_product(self):
        # drf-nested-routers stores the company pk in kwargs
        return get_object_or_404(Product, pk=self.kwargs['product_pk'], supplier=self.get_parent_company())

    def get_queryset(self):
        product = self.get_parent_product()
        qs = ProductBoMLineItem.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        product = self.get_parent_product()
        serializer.save(parent_product=product)

    @extend_schema(
        tags=["Product BoM line items"],
        summary="Retrieve all BoM line items for a product",
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        tags=["Product BoM line items"],
        summary="Retrieve a specific BoM line item for a product",
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @extend_schema(
        tags=["Product BoM line items"],
        summary="Create a new BoM line item for a product",
    )
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)

    @extend_schema(
        tags=["Product BoM line items"],
        summary="Update a BoM line item for a product",
    )
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

    @extend_schema(
        tags=["Product BoM line items"],
        summary="Partially update a BoM line item for a product",
    )
    def partial_update(self, *args, **kwargs):
        return super().partial_update(*args, **kwargs)

    @extend_schema(
        tags=["Product BoM line items"],
        summary="Delete a BoM line item for a product",
    )
    def destroy(self, *args, **kwargs):
        return super().destroy(*args, **kwargs)