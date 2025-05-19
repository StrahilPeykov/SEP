from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.generics import get_object_or_404

from core.models import Company, Product
from core.models.transport_emission import TransportEmission
from core.permissions import ProductSubAPIPermission
from core.serializers.emission_serializers import TransportEmissionSerializer
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
    ],
)
@extend_schema_view(
    list=extend_schema(
        tags=["Emissions/Transport"],
        summary="List all transport emissions",
        description="Retrieve a list of all transport emissions associated with a specific product."
    ),
    retrieve=extend_schema(
        tags=["Emissions/Transport"],
        summary="Retrieve a transport emission",
        description="Retrieve the details of a specific transport emission by its ID."
    ),
    create=extend_schema(
        tags=["Emissions/Transport"],
        summary="Create a transport emission",
        description="Create a new transport emission associated with a specific product."
    ),
    update=extend_schema(
        tags=["Emissions/Transport"],
        summary="Update a transport emission",
        description="Update the details of a specific transport emission by its ID."
    ),
    partial_update=extend_schema(
        tags=["Emissions/Transport"],
        summary="Partially update a transport emission",
        description="Partially update the details of a specific transport emission by its ID."
    ),
    destroy=extend_schema(
        tags=["Emissions/Transport"],
        summary="Delete a transport emission",
        description="Delete a specific transport emission by its ID."
    ),
)
class TransportEmissionViewSet(
    CompanyMixin,
    ProductMixin,
    viewsets.ModelViewSet
):
    queryset = TransportEmission.objects.all()
    serializer_class = TransportEmissionSerializer
    permission_classes = [permissions.IsAuthenticated, ProductSubAPIPermission]

    def get_queryset(self):
        product = self.get_parent_product()
        qs = TransportEmission.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        product = self.get_parent_product()
        serializer.save(parent_product=product)