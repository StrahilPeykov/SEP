from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, extend_schema_field, OpenApiParameter
from rest_framework.generics import get_object_or_404

from core.models import Company, Product
from core.models.production_energy_emission import ProductionEnergyEmission
from core.permissions import ProductSubAPIPermission
from core.resources.emission_resources import ProductionEnergyEmissionResource
from core.serializers.emission_serializers import ProductionEnergyEmissionSerializer
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
        tags=["Emissions/Production energy"],
        summary="List all production energy emissions",
        description="Retrieve a list of all production energy emissions associated with a specific product."
    ),
    retrieve=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Retrieve a production energy emission",
        description="Retrieve the details of a specific production energy emission by its ID."
    ),
    create=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Create a production energy emission",
        description="Create a new production energy emission associated with a specific product."
    ),
    update=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Update a production energy emission",
        description="Update the details of a specific production energy emission by its ID."
    ),
    partial_update=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Partially update a production energy emission",
        description="Partially update the details of a specific production energy emission by its ID."
    ),
    destroy=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Delete a production energy emission",
        description="Delete a specific production energy emission by its ID."
    ),
    export_csv=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Export production energy emissions to CSV",
        description=(
                "Export all this product's production energy emissions to CSV format. "
                "The CSV file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'text/csv'): OpenApiTypes.STR,
        }
    ),
    export_xlsx=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Export production energy emissions to XLSX",
        description=(
                "Export all this product's production energy emissions to XLSX format. "
                "The CSV file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'): OpenApiTypes.BINARY,
        }
    ),
    import_tabular=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Import production energy emissions",
        description="Import production energy emissions from a tabular file."
    ),
)
class ProductionEnergyEmissionViewSet(
    CompanyMixin,
    ProductMixin,
    EmissionImportExportMixin,
    viewsets.ModelViewSet
):
    queryset = ProductionEnergyEmission.objects.all()
    serializer_class = ProductionEnergyEmissionSerializer
    permission_classes = [permissions.IsAuthenticated, ProductSubAPIPermission]
    emission_import_export_resource = ProductionEnergyEmissionResource

    def get_queryset(self):
        product = self.get_parent_product()
        qs = ProductionEnergyEmission.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        product = self.get_parent_product()
        serializer.save(parent_product=product)