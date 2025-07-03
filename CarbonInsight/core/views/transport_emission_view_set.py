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
    #Extend schema with list method, allowing the listing of all transport emissions of a specific product.
        tags=["Emissions/Transport"],
        summary="List all transport emissions",
        description="Retrieve a list of all transport emissions associated with a specific product."
    ),
    #Extend schema with retrieve method, allowing the listing of a specific transport emissions of a product.
    retrieve=extend_schema(
        tags=["Emissions/Transport"],
        summary="Retrieve a transport emission",
        description="Retrieve the details of a specific transport emission by its ID."
    ),
    #Extend schema with create method, allowing the creation of a transport emission for a specific product.
    create=extend_schema(
        tags=["Emissions/Transport"],
        summary="Create a transport emission",
        description="Create a new transport emission associated with a specific product."
    ),
    #Extend schema with update method, allowing the update of a specific transport emission of a product.
    update=extend_schema(
        tags=["Emissions/Transport"],
        summary="Update a transport emission",
        description="Update the details of a specific transport emission by its ID."
    ),
    #Extend schema with partial_update method, allowing the partial update of a transport emission of a product.
    partial_update=extend_schema(
        tags=["Emissions/Transport"],
        summary="Partially update a transport emission",
        description="Partially update the details of a specific transport emission by its ID."
    ),
    #Extend schema with destroy method, allowing the deletion of a specific transport emission of a product.
    destroy=extend_schema(
        tags=["Emissions/Transport"],
        summary="Delete a transport emission",
        description="Delete a specific transport emission by its ID."
    ),
    #Extend schema with export_csv method, allowing the export of a specific transport emission of a product in csv
    # format.
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
    #Extend schema with export_xlsx method, allowing the export of a specific transport emission of a product in xlsx
    # format.
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
    #Extend schema with import_tubular method, allowing the import of transport emissions for a product in
    # .csv, .xls or .xlsx formats.
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
    """
    Provides methods that manage CRUD operations and import/export for transport emissions linked to a product in order
     to avoid duplicate code.
    """
    queryset = TransportEmission.objects.all()
    serializer_class = TransportEmissionSerializer
    permission_classes = [permissions.IsAuthenticated, ProductSubAPIPermission]
    emission_import_export_resource = TransportEmissionResource

    def get_queryset(self):
        """
        Retrieves the queryset of transport emissions filtered by the parent product.

        Returns:
            QuerySet: A queryset of TransportEmission instances related to the product.
        """
        product = self.get_parent_product()
        qs = TransportEmission.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        """
        Performs the creation of a new transport emission, associating it with the parent product.

        Args:
            serializer (TransportEmissionSerializer): The serializer instance containing validated data.
        """
        product = self.get_parent_product()
        serializer.save(parent_product=product)
