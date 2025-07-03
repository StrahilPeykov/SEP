from io import BytesIO

from auditlog.models import LogEntry
from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from core.importers.aas_validators import validate_aas_aasx, validate_aas_json, validate_aas_xml
from core.models import Product
from core.permissions import ProductPermission, ProductSubAPIPermission
from core.resources.product_resource import ProductResource
from core.serializers.product_serializer import ProductSerializer
from core.views.mixins.company_mixin import CompanyMixin


class ProductExportViewSet(
    CompanyMixin,
    viewsets.GenericViewSet
):
    """
    Manages product exports in various formats including AAS AASX, AAS XML, AAS JSON, SCSN XML, CSV, and XLSX.
    """
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, ProductPermission]


    @extend_schema(
        tags=["Products"],
        summary="Export product to AAS AASX format",
        description=(
                "Export the product data to AAS AASX format. "
                "This includes its PCF and Digital Nameplate. "
                "The AASX file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'application/asset-administration-shell-package'): OpenApiTypes.BINARY,
        }
    )
    @action(detail=True, methods=["get"],
            permission_classes=[IsAuthenticated, ProductSubAPIPermission],
            url_path="export/aas_aasx")
    def export_aas_aasx(self, request, *args, **kwargs):
        """
        Exports the product data to AAS AASX format, including PCF and Digital Nameplate.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, including the product's primary key.

        Returns:
            FileResponse: A downloadable AASX file.
        """
        product = self.get_object()
        file = product.export_to_aas_aasx()
        validate_aas_aasx(file)
        LogEntry.objects.log_create(instance=product, force_log=True, action=LogEntry.Action.ACCESS, changes_text="Exported to AAS AASX format")
        return FileResponse(
            file,
            as_attachment=True,
            filename=f"{product.name}_aas.aasx",
            content_type="application/asset-administration-shell-package",
        )

    @extend_schema(
        tags=["Products"],
        summary="Export product to AAS XML format",
        description=(
                "Export the product data to AAS XML format. "
                "This includes its PCF and Digital Nameplate. "
                "The XML file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'application/xml'): OpenApiTypes.STR,
        }
    )
    @action(detail=True, methods=["get"],
            permission_classes=[IsAuthenticated, ProductSubAPIPermission],
            url_path="export/aas_xml")
    def export_aas_xml(self, request, *args, **kwargs):
        """
        Exports the product data to AAS XML format, including PCF and Digital Nameplate.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, including the product's primary key.

        Returns:
            FileResponse: A downloadable XML file.
        """
        product = self.get_object()
        file = product.export_to_aas_xml()
        validate_aas_xml(file)
        LogEntry.objects.log_create(instance=product, force_log=True, action=LogEntry.Action.ACCESS, changes_text="Exported to AAS XML format")
        return FileResponse(
            file,
            as_attachment=True,
            filename=f"{product.name}_aas.xml",
            content_type="application/xml",
        )

    @extend_schema(
        tags=["Products"],
        summary="Export product to AAS JSON format",
        description=(
                "Export the product data to AAS JSON format. "
                "This includes its PCF and Digital Nameplate. "
                "The JSON file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'application/json'): OpenApiTypes.STR,
        }
    )
    @action(detail=True, methods=["get"],
            permission_classes=[IsAuthenticated, ProductSubAPIPermission],
            url_path="export/aas_json")
    def export_aas_json(self, request, *args, **kwargs) -> FileResponse:
        """
        Exports the product data to AAS JSON format, including PCF and Digital Nameplate.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, including the product's primary key.

        Returns:
            FileResponse: A downloadable JSON file.
        """
        product = self.get_object()
        file = product.export_to_aas_json()
        validate_aas_json(file)
        LogEntry.objects.log_create(instance=product, force_log=True, action=LogEntry.Action.ACCESS, changes_text="Exported to AAS JSON format")
        return FileResponse(
            file,
            as_attachment=True,
            filename=f"{product.name}_aas.json",
            content_type="application/json",
        )

    @extend_schema(
        tags=["Products"],
        summary="Export product PCF to SCSN XML format (partial)",
        description=(
                "Export the product's PCF data to SCSN XML format. "
                "The XML file will be returned as a downloadable attachment. "
                "The returned file is NOT SCSN compliant. It only includes the PCF data. "
                "The user is expected to append our data to their own SCSN XML file. "
        ),
        responses={
            (200, 'application/xml'): OpenApiTypes.STR,
        }
    )
    @action(detail=True, methods=["get"],
            permission_classes=[IsAuthenticated, ProductSubAPIPermission],
            url_path="export/scsn_pcf_xml")
    def export_scsn_pcf_xml(self, request, *args, **kwargs):
        """
        Exports the product's PCF data to a partial SCSN XML format.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, including the product's primary key.

        Returns:
            FileResponse: A downloadable XML file containing partial SCSN PCF data.
        """
        product = self.get_object()
        file = product.export_to_scsn_pcf_xml()
        LogEntry.objects.log_create(instance=product, force_log=True, action=LogEntry.Action.ACCESS, changes_text="Exported to SCSN XML format (partial)")
        return FileResponse(
            file,
            as_attachment=True,
            filename=f"{product.name}_scsn_pcf.xml",
            content_type="application/xml",
        )

    @extend_schema(
        tags=["Products"],
        summary="Export product PCF to SCSN XML format (full)",
        description=(
                "Export the product's PCF data to SCSN XML format. "
                "The XML file will be returned as a downloadable attachment."
                "The returned file is SCSN compliant but with placeholders for certain fields. "
        ),
        responses={
            (200, 'application/xml'): OpenApiTypes.STR,
        }
    )
    @action(detail=True, methods=["get"],
            permission_classes=[IsAuthenticated, ProductSubAPIPermission],
            url_path="export/scsn_full_xml")
    def export_scsn_full_xml(self, request, *args, **kwargs):
        """
        Exports the product's PCF data to a full SCSN XML format with placeholders.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, including the product's primary key.

        Returns:
            FileResponse: A downloadable XML file containing full SCSN PCF data with placeholders.
        """
        product = self.get_object()
        file = product.export_to_scsn_full_xml()
        LogEntry.objects.log_create(instance=product, force_log=True, action=LogEntry.Action.ACCESS, changes_text="Exported to SCSN XML format (full)")
        return FileResponse(
            file,
            as_attachment=True,
            filename=f"{product.name}_scsn_full.xml",
            content_type="application/xml",
        )

    @extend_schema(
        tags=["Products"],
        summary="Export product to ZIP",
        description=(
                "Export the product's data as a ZIP archive of all other exporters. "
                "The ZIP file will be returned as a downloadable attachment."
        ),
        responses={
            (200, 'application/zip'): OpenApiTypes.BINARY,
        }
    )
    @action(detail=True, methods=["get"],
            permission_classes=[IsAuthenticated, ProductSubAPIPermission],
            url_path="export/zip")
    def export_zip(self, request, *args, **kwargs):
        """
        Exports the product's data as a ZIP archive containing files from other exporters.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, including the product's primary key.

        Returns:
            FileResponse: A downloadable ZIP archive of the product's data.
        """
        product = self.get_object()
        file = product.export_to_zip()
        LogEntry.objects.log_create(instance=product, force_log=True, action=LogEntry.Action.ACCESS,
                                    changes_text="Exported to ZIP")
        return FileResponse(
            file,
            as_attachment=True,
            filename=f"{product.name}.zip",
            content_type="application/zip",
        )



    @extend_schema(
        tags=["Products"],
        summary="Export all products to CSV",
        description=(
            "Export all this company's products to CSV format. "
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
    )
    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticated, ProductPermission],
            url_path="export/csv")
    def export_csv(self, request, *args, **kwargs):
        """
        Exports all products of the company to CSV format.

        Args:
            request (HttpRequest): The HTTP request object, possibly containing a 'template' query parameter.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            FileResponse: A downloadable CSV file containing product data or an empty template.
        """
        # Check if template is requested
        if request.query_params.get("template", "false").lower() == "true":
            queryset = self.get_queryset()[:0]  # Empty queryset for template
        else:
            queryset = self.get_queryset()
        dataset = ProductResource().export(queryset=queryset)
        csv_bytes = dataset.csv.encode("utf-8")
        file_io = BytesIO(csv_bytes)
        LogEntry.objects.log_create(instance=self.get_parent_company(), force_log=True, action=LogEntry.Action.ACCESS, changes_text="Exported to CSV format")
        return FileResponse(
            file_io,
            as_attachment=True,
            filename=f"{self.get_parent_company().name}_products.csv",
            content_type="text/csv",
        )

    @extend_schema(
        tags=["Products"],
        summary="Export all products to XLSX",
        description=(
                "Export all this company's products to XLSX format. "
                "The XLSX file will be returned as a downloadable attachment."
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
    )
    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticated, ProductPermission],
            url_path="export/xlsx")
    def export_xlsx(self, request, *args, **kwargs):
        """
        Exports all products of the company to XLSX format.

        Args:
            request (HttpRequest): The HTTP request object, possibly containing a 'template' query parameter.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            FileResponse: A downloadable XLSX file containing product data or an empty template.
        """
        # Check if template is requested
        if request.query_params.get("template", "false").lower() == "true":
            queryset = self.get_queryset()[:0]  # Empty queryset for template
        else:
            queryset = self.get_queryset()
        dataset = ProductResource().export(queryset=queryset)
        result = dataset.export(format="xlsx")
        file_io = BytesIO(result)
        LogEntry.objects.log_create(instance=self.get_parent_company(), force_log=True, action=LogEntry.Action.ACCESS, changes_text="Exported to XLSX format")
        return FileResponse(
            file_io,
            as_attachment=True,
            filename=f"{self.get_parent_company().name}_products.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )