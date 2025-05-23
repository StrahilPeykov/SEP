from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from core.models import Company, Product
from core.models.user_energy_emission import UserEnergyEmission
from core.permissions import ProductSubAPIPermission, ProductPermission
from core.resources.emission_resources import UserEnergyEmissionResource
from core.serializers.emission_serializers import UserEnergyEmissionSerializer
from core.views.mixins.company_mixin import CompanyMixin
from core.views.mixins.emission_import_export_mixin import EmissionImportExportMixin
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
        tags=["Emissions/User energy"],
        summary="List all user energy emissions",
        description="Retrieve a list of all user energy emissions associated with a specific product."
    ),
    retrieve=extend_schema(
        tags=["Emissions/User energy"],
        summary="Retrieve a user energy emission",
        description="Retrieve the details of a specific user energy emission by its ID."
    ),
    create=extend_schema(
        tags=["Emissions/User energy"],
        summary="Create a user energy emission",
        description="Create a new user energy emission associated with a specific product."
    ),
    update=extend_schema(
        tags=["Emissions/User energy"],
        summary="Update a user energy emission",
        description="Update the details of a specific user energy emission by its ID."
    ),
    partial_update=extend_schema(
        tags=["Emissions/User energy"],
        summary="Partially update a user energy emission",
        description="Partially update the details of a specific user energy emission by its ID."
    ),
    destroy=extend_schema(
        tags=["Emissions/User energy"],
        summary="Delete a user energy emission",
        description="Delete a specific user energy emission by its ID."
    ),
    export_csv=extend_schema(
        tags=["Emissions/User energy"],
        summary="Export user energy emissions to CSV",
        description=(
                "Export all this product's user energy emissions to CSV format. "
                "The CSV file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'text/csv'): OpenApiTypes.STR,
        }
    ),
    export_xlsx=extend_schema(
        tags=["Emissions/User energy"],
        summary="Export user energy emissions to XLSX",
        description=(
                "Export all this product's user energy emissions to XLSX format. "
                "The CSV file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'): OpenApiTypes.BINARY,
        }
    ),
    import_tabular=extend_schema(
        tags=["Emissions/User energy"],
        summary="Import user energy emissions",
        description="Import user energy emissions from a tabular file."
    ),
)
class UserEnergyEmissionViewSet(
    CompanyMixin,
    ProductMixin,
    EmissionImportExportMixin,
    viewsets.ModelViewSet
):
    queryset = UserEnergyEmission.objects.all()
    serializer_class = UserEnergyEmissionSerializer
    permission_classes = [permissions.IsAuthenticated, ProductSubAPIPermission]
    emission_import_export_resource = UserEnergyEmissionResource

    def get_queryset(self):
        product = self.get_parent_product()
        qs = UserEnergyEmission.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        product = self.get_parent_product()
        serializer.save(parent_product=product)