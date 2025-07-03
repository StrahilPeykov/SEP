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
    #Extend schema with list method, allowing the listing of all user energy emissions of a specific product.
        tags=["Emissions/User energy"],
        summary="List all user energy emissions",
        description="Retrieve a list of all user energy emissions associated with a specific product."
    ),
    #Extend schema with retrieve method, allowing the listing of a specific user energy emissions of a product.
    retrieve=extend_schema(
        tags=["Emissions/User energy"],
        summary="Retrieve a user energy emission",
        description="Retrieve the details of a specific user energy emission by its ID."
    ),
    #Extend schema with create method, allowing the creation of a user energy emission for a specific product.
    create=extend_schema(
        tags=["Emissions/User energy"],
        summary="Create a user energy emission",
        description="Create a new user energy emission associated with a specific product."
    ),
    #Extend schema with update method, allowing the update of a specific user energy emission of a product.
    update=extend_schema(
        tags=["Emissions/User energy"],
        summary="Update a user energy emission",
        description="Update the details of a specific user energy emission by its ID."
    ),
    #Extend schema with partial_update method, allowing the partial update of a specific user energy emission of a
    # product.
    partial_update=extend_schema(
        tags=["Emissions/User energy"],
        summary="Partially update a user energy emission",
        description="Partially update the details of a specific user energy emission by its ID."
    ),
    #Extend schema with destroy method, allowing the deletion of a specific user energy emission of a product.
    destroy=extend_schema(
        tags=["Emissions/User energy"],
        summary="Delete a user energy emission",
        description="Delete a specific user energy emission by its ID."
    ),
    #Extend schema with export_csv method, allowing the export of a specific user energy emission of a product in
    # csv format.
    export_csv=extend_schema(
        tags=["Emissions/User energy"],
        summary="Export user energy emissions to CSV",
        description=(
                "Export all this product's user energy emissions to CSV format. "
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
    #Extend schema with export_xlsx method, allowing the export of a specific user energy emission of a product in
    # xlsx format.
    export_xlsx=extend_schema(
        tags=["Emissions/User energy"],
        summary="Export user energy emissions to XLSX",
        description=(
                "Export all this product's user energy emissions to XLSX format. "
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
    #Extend schema with import_tubular method, allowing the import of user energy emissions for a product in
    # .csv, .xls or .xlsx formats.
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
    """
    Provides methods that manage CRUD operations and import/export for user energy emissions linked to a product in
     order avoid duplicate code.
    """
    queryset = UserEnergyEmission.objects.all()
    serializer_class = UserEnergyEmissionSerializer
    permission_classes = [permissions.IsAuthenticated, ProductSubAPIPermission]
    emission_import_export_resource = UserEnergyEmissionResource

    def get_queryset(self):
        """
        Retrieves the queryset of user energy emissions filtered by the parent product.

        Returns:
            QuerySet: A queryset of UserEnergyEmission instances related to the product.
        """
        product = self.get_parent_product()
        qs = UserEnergyEmission.objects.filter(parent_product=product)
        return qs

    def perform_create(self, serializer):
        """
        Performs the creation of a new user energy emission, associating it with the parent product.

        Args:
            serializer (UserEnergyEmissionSerializer): The serializer instance containing validated data.
        """
        product = self.get_parent_product()
        serializer.save(parent_product=product)