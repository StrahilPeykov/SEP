from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from core.models import Product, Company
from core.permissions import ProductPermission
from core.serializers.product_serializer import ProductSerializer
from core.serializers.product_sharing_request_serializer import ProductSharingRequestRequestAccessSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, ProductPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'description', 'manufacturer', 'sku', 'is_public']
    search_fields = ['name', 'description', 'manufacturer', 'sku']

    def get_serializer_class(self):
        if self.action in ["request_access"]:
            return ProductSharingRequestRequestAccessSerializer
        return super().get_serializer_class()

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
        tags=["Products"],
        summary="Create a new product",
        description=(
            "Create a new product with the given details with `company_pk` as the supplier."
        )
    )
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)

    @extend_schema(
        tags=["Products"],
        summary="Retrieve all products",
        description=(
            "Retrieve the details of all products with `company_pk` as the supplier."
        )
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        tags=["Products"],
        summary="Retrieve a specific product",
        description=(
            "Retrieve the details of a specific product by its ID."
        )
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @extend_schema(
        tags=["Products"],
        summary="Partially update a specific product's details",
        description=(
            "Update the details of a specific product by its ID. "
            "Only the fields that are provided in the request body will be updated."
        )
    )
    def partial_update(self, *args, **kwargs):
        return super().partial_update(*args, **kwargs)

    @extend_schema(
        tags=["Products"],
        summary="Update a specific product's details",
        description=(
            "Update the details of a specific product by its ID. "
            "All fields will be updated with the provided values."
        )
    )
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

    @extend_schema(
        tags=["Products"],
        summary="Delete a specific product",
        description=(
            "Delete a specific product by its ID."
        )
    )
    def destroy(self, *args, **kwargs):
        return super().destroy(*args, **kwargs)

    @extend_schema(
        tags=["Products"],
        summary="Request access to product emissions",
        description="Request access to the carbon emissions of a specific product "
                    "on behalf of a company the current user is a member of.",
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def request_access(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = Company.objects.get(pk=serializer.data.get("requester"))
        user = request.user

        if not company.user_is_member(user):
            return Response(
                {"detail": "You are not a member of this company."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Try to request access
        try:
            product.request(
                requester=company,
                user=user,
            )
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
