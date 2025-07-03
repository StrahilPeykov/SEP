from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
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
    #Extend schema with list method, allowing the listing of all production energy emissions of a specific product.
    list=extend_schema(
        tags=["Emissions/Production energy"],
        summary="List all production energy emissions",
        description="Retrieve a list of all production energy emissions associated with a specific product."
    ),
    #Extend schema with retrieve method, allowing the listing of a specific production energy emissions of a product.
    retrieve=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Retrieve a production energy emission",
        description="Retrieve the details of a specific production energy emission by its ID."
    ),
    #Extend schema with create method, allowing the creation of a production energy emission for a specific product.
    create=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Create a production energy emission",
        description="Create a new production energy emission associated with a specific product."
    ),
    #Extend schema with update method, allowing the update of a specific production energy emission of a product.
    update=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Update a production energy emission",
        description="Update the details of a specific production energy emission by its ID."
    ),
    #Extend schema with partial_update method, allowing the partial update of a specific production energy emission of a
    # product.
    partial_update=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Partially update a production energy emission",
        description="Partially update the details of a specific production energy emission by its ID."
    ),
    #Extend schema with destroy method, allowing the deletion of a specific production energy emission of a product.
    destroy=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Delete a production energy emission",
        description="Delete a specific production energy emission by its ID."
    ),
    #Extend schema with export_csv method, allowing the export of a specific production energy emission of a product in
    # csv format.
    export_csv=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Export production energy emissions to CSV",
        description=(
                "Export all this product's production energy emissions to CSV format. "
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
    #Extend schema with export_xlsx method, allowing the export of a specific production energy emission of a product in
    # xlsx format.
    export_xlsx=extend_schema(
        tags=["Emissions/Production energy"],
        summary="Export production energy emissions to XLSX",
        description=(
                "Export all this product's production energy emissions to XLSX format. "
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
    #Extend schema with import_tubular method, allowing the import of production energy emissions for a product in
    # .csv, .xls or .xlsx formats.
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
    """
    Provides methods that manage CRUD operations and import/export for production energy emissions linked to a product
     in order to avoid duplicate code.
    """
    queryset = ProductionEnergyEmission.objects.all()
    serializer_class = ProductionEnergyEmissionSerializer
    permission_classes = [permissions.IsAuthenticated, ProductSubAPIPermission]
    emission_import_export_resource = ProductionEnergyEmissionResource

    def get_queryset(self):
        """
        Retrieves the queryset of production energy emissions filtered by the parent product.

        Returns:
            QuerySet: A queryset of ProductionEnergyEmission instances related to the product.
        """
        product = self.get_parent_product()
        qs = ProductionEnergyEmission.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        """
        Performs the creation of a new production energy emission, associating it with the parent product.

        Args:
            serializer (ProductionEnergyEmissionSerializer): The serializer instance containing validated data.
        """
        product = self.get_parent_product()
        serializer.save(parent_product=product)