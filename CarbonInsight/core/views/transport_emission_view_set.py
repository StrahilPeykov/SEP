from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from core.models.transport_emission import TransportEmission
from core.permissions import ProductSubAPIPermission, ProductPermission
from core.resources.emission_resources import TransportEmissionResource
from core.serializers.emission_serializers import TransportEmissionSerializer
from core.views.mixins.company_mixin import CompanyMixin
from core.views.mixins.emission_import_export_mixin import EmissionImportExportMixin, T
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
    export_csv=extend_schema(
        tags=["Emissions/Transport"],
        summary="Export transport emissions to CSV",
        description=(
                "Export all this product's transport emissions to CSV format. "
                "The CSV file will be returned as a downloadable attachment."
        ),
        parameters=[
            OpenApiParameter(
                name="template",
                type=OpenApiTypes.BOOL,
                location="query",
                description="If true, return only the header row as an empty template.",
                required=False,
            ),
        ],
        responses={
            (200, 'text/csv'): OpenApiTypes.STR,
        }
    ),
    export_xlsx=extend_schema(
        tags=["Emissions/Transport"],
        summary="Export transport emissions to XLSX",
        description=(
                "Export all this product's transport emissions to XLSX format. "
                "The CSV file will be returned as a downloadable attachment."
        ),
        parameters=[
            OpenApiParameter(
                name="template",
                type=OpenApiTypes.BOOL,
                location="query",
                description="If true, return only the header row as an empty template.",
                required=False,
            ),
        ],
        responses={
            (200, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'): OpenApiTypes.BINARY,
        }
    ),
    import_tabular=extend_schema(
        tags=["Emissions/Transport"],
        summary="Import transport emissions",
        description="Import transport emissions from a tabular file."
    ),
)
class TransportEmissionViewSet(
    CompanyMixin,
    ProductMixin,
    EmissionImportExportMixin,
    viewsets.ModelViewSet
):
    queryset = TransportEmission.objects.all()
    serializer_class = TransportEmissionSerializer
    permission_classes = [permissions.IsAuthenticated, ProductSubAPIPermission]
    emission_import_export_resource = TransportEmissionResource

    def get_queryset(self):
        product = self.get_parent_product()
        qs = TransportEmission.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        product = self.get_parent_product()
        serializer.save(parent_product=product)
