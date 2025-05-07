from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from core.models import Product, Company
from core.permissions import ProductPermission
from core.serializers.product_serializer import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, ProductPermission]

    def get_parent_company(self):
        # drf-nested-routers stores the company pk in kwargs
        return Company.objects.get(pk=self.kwargs['company_pk'])

    def get_queryset(self):
        company = self.get_parent_company()
        qs = Product.objects.filter(supplier=company)
        user = self.request.user

        # If listing with a non-member user, only show public
        if self.request.method in SAFE_METHODS and not company.user_is_member(user):
            return qs.filter(is_public=True)
        return qs

    def perform_create(self, serializer):
        company = self.get_parent_company()
        serializer.save(supplier=company)

    @extend_schema(
        summary="Create a new product",
        description=(
            "Create a new product with the given details with `company_pk` as the supplier."
        )
    )
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)

    @extend_schema(
        summary="Retrieve all products",
        description=(
            "Retrieve the details of all products with `company_pk` as the supplier."
        )
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        summary="Retrieve a specific product",
        description=(
            "Retrieve the details of a specific product by its ID."
        )
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @extend_schema(
        summary="Partially update a specific product's details",
        description=(
            "Update the details of a specific product by its ID. "
            "Only the fields that are provided in the request body will be updated."
        )
    )
    def partial_update(self, *args, **kwargs):
        return super().partial_update(*args, **kwargs)

    @extend_schema(
        summary="Update a specific product's details",
        description=(
            "Update the details of a specific product by its ID. "
            "All fields will be updated with the provided values."
        )
    )
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

    @extend_schema(
        summary="Delete a specific product",
        description=(
            "Delete a specific product by its ID."
        )
    )
    def destroy(self, *args, **kwargs):
        return super().destroy(*args, **kwargs)

