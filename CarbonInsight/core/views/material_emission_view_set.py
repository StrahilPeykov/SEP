from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.generics import get_object_or_404

from core.models import Company, Product
from core.models.material_emission import MaterialEmission
from core.permissions import ProductSubAPIPermission
from core.resources.emission_resources import MaterialEmissionResource
from core.serializers.emission_serializers import MaterialEmissionSerializer
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
        tags=["Emissions/Material"],
        summary="List all material emissions",
        description="Retrieve a list of all material emissions associated with a specific product."
    ),
    retrieve=extend_schema(
        tags=["Emissions/Material"],
        summary="Retrieve a material emission",
        description="Retrieve the details of a specific material emission by its ID."
    ),
    create=extend_schema(
        tags=["Emissions/Material"],
        summary="Create a material emission",
        description="Create a new material emission associated with a specific product."
    ),
    update=extend_schema(
        tags=["Emissions/Material"],
        summary="Update a material emission",
        description="Update the details of a specific material emission by its ID."
    ),
    partial_update=extend_schema(
        tags=["Emissions/Material"],
        summary="Partially update a material emission",
        description="Partially update the details of a specific material emission by its ID."
    ),
    destroy=extend_schema(
        tags=["Emissions/Material"],
        summary="Delete a material emission",
        description="Delete a specific material emission by its ID."
    ),
    export_csv=extend_schema(
        tags=["Emissions/Material"],
        summary="Export material emissions to CSV",
        description=(
                "Export all this product's material emissions to CSV format. "
                "The CSV file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'text/csv'): OpenApiTypes.STR,
        }
    ),
    export_xlsx=extend_schema(
        tags=["Emissions/Material"],
        summary="Export material emissions to XLSX",
        description=(
                "Export all this product's material emissions to XLSX format. "
                "The CSV file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'): OpenApiTypes.BINARY,
        }
    ),
    import_tabular=extend_schema(
        tags=["Emissions/Material"],
        summary="Import material emissions",
        description="Import material emissions from a tabular file."
    ),
)
class MaterialEmissionViewSet(
    CompanyMixin,
    ProductMixin,
    EmissionImportExportMixin,
    viewsets.ModelViewSet
):
    queryset = MaterialEmission.objects.all()
    serializer_class = MaterialEmissionSerializer
    permission_classes = [permissions.IsAuthenticated, ProductSubAPIPermission]
    emission_import_export_resource = MaterialEmissionResource

    def get_queryset(self):
        product = self.get_parent_product()
        qs = MaterialEmission.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        product = self.get_parent_product()
        serializer.save(parent_product=product)