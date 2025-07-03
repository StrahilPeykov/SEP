from io import BytesIO

from django.core.validators import FileExtensionValidator
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.utils import inline_serializer
from import_export.results import RowResult
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, UnsupportedMediaType
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from tablib import Dataset

from core.importers.aas import aas_aasx_to_db, aas_json_to_db, aas_xml_to_db
from core.models import Product
from core.permissions import ProductPermission
from core.resources.product_resource import ProductResource
from core.serializers.product_serializer import ProductSerializer
from core.views.mixins.company_mixin import CompanyMixin


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="company_pk",
            type=int,
            location="path",
            description="Primary key of the parent Company",
        ),
    ],
)

class ProductImportViewSet(
    CompanyMixin,
    viewsets.GenericViewSet
):
    """
    Manages CRUD operations and related actions for products within a company.
    """
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, ProductPermission]

    @extend_schema(
        tags=["Products"],
        summary="Create product from AAS AASX file",
        description=(
                "Creates a new product from an uploaded AAS AASX file. "
                "The file should be uploaded as a multipart/form-data request with the key 'file'."
        ),
        request=inline_serializer(
            name="InlineUploadAASAASXSerializer",
            fields={"file": serializers.FileField()},
        ),
    )
    @action(detail=False, methods=["post"],
            parser_classes=[MultiPartParser],
            permission_classes=[IsAuthenticated, ProductPermission],
            url_path="import/aas_aasx")
    def import_aas_aasx(self, request, *args, **kwargs):
        """
        Creates a new product by importing data from an uploaded AAS AASX file.

        Args:
            request (HttpRequest): The HTTP request object containing the AASX file.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP 201 Created response with the serialized new product data.

        Raises:
            ValidationError: If no file or more than one file is uploaded.
            UnsupportedMediaType: If the uploaded file has an invalid extension.
        """
        # Ensure exactly one file was sent
        if 'file' not in request.FILES or len(request.FILES) != 1:
            raise ValidationError({"file": "Please upload exactly one file under the 'file' key."})

        uploaded = request.FILES['file']

        # Validate extension
        validator = FileExtensionValidator(allowed_extensions=['aasx'])
        try:
            validator(uploaded)
        except ValidationError:
            raise UnsupportedMediaType("Invalid file extension. Only .aasx is allowed.")

        # Read into BytesIO
        file_bytes = uploaded.read()
        file_io = BytesIO(file_bytes)

        product = aas_aasx_to_db(file_io, self.get_parent_company())

        # Serialize and return the newly created Product
        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Products"],
        summary="Create product from AAS JSON file",
        description=(
                "Creates a new product from an uploaded AAS JSON file. "
                "The file should be uploaded as a multipart/form-data request with the key 'file'."
        ),
        request=inline_serializer(
            name="InlineUploadAASJSONSerializer",
            fields={"file": serializers.FileField()},
        ),
    )
    @action(detail=False, methods=["post"],
            parser_classes=[MultiPartParser],
            permission_classes=[IsAuthenticated, ProductPermission],
            url_path="import/aas_json")
    def import_aas_json(self, request, *args, **kwargs):
        """
        Creates a new product by importing data from an uploaded AAS JSON file.

        Args:
            request (HttpRequest): The HTTP request object containing the JSON file.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP 201 Created response with the serialized new product data.

        Raises:
            ValidationError: If no file or more than one file is uploaded.
            UnsupportedMediaType: If the uploaded file has an invalid extension.
        """
        # Ensure exactly one file was sent
        if 'file' not in request.FILES or len(request.FILES) != 1:
            raise ValidationError({"file": "Please upload exactly one file under the 'file' key."})

        uploaded = request.FILES['file']

        # Validate extension
        validator = FileExtensionValidator(allowed_extensions=['json'])
        try:
            validator(uploaded)
        except ValidationError:
            raise UnsupportedMediaType("Invalid file extension. Only .json is allowed.")

        # Read into BytesIO
        file_bytes = uploaded.read()
        file_io = BytesIO(file_bytes)

        product = aas_json_to_db(file_io, self.get_parent_company())

        # Serialize and return the newly created Product
        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Products"],
        summary="Create product from AAS XML file",
        description=(
                "Creates a new product from an uploaded AAS XML file. "
                "The file should be uploaded as a multipart/form-data request with the key 'file'."
        ),
        request=inline_serializer(
            name="InlineUploadAASXMLSerializer",
            fields={"file": serializers.FileField()},
        ),
    )
    @action(detail=False, methods=["post"],
            parser_classes=[MultiPartParser],
            permission_classes=[IsAuthenticated, ProductPermission],
            url_path="import/aas_xml")
    def import_aas_xml(self, request, *args, **kwargs):
        """
        Creates a new product by importing data from an uploaded AAS XML file.

        Args:
            request (HttpRequest): The HTTP request object containing the XML file.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP 201 Created response with the serialized new product data.

        Raises:
            ValidationError: If no file or more than one file is uploaded.
            UnsupportedMediaType: If the uploaded file has an invalid extension.
        """
        # Ensure exactly one file was sent
        if 'file' not in request.FILES or len(request.FILES) != 1:
            raise ValidationError({"file": "Please upload exactly one file under the 'file' key."})

        uploaded = request.FILES['file']

        # Validate extension
        validator = FileExtensionValidator(allowed_extensions=['xml'])
        try:
            validator(uploaded)
        except ValidationError:
            raise UnsupportedMediaType("Invalid file extension. Only .xml is allowed.")

        # Read into BytesIO
        file_bytes = uploaded.read()
        file_io = BytesIO(file_bytes)

        product = aas_xml_to_db(file_io, self.get_parent_company())

        # Serialize and return the newly created Product
        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Products"],
        summary="Import products from tabular file",
        description=(
                "Import products from a CSV, XLS or XLSX file. "
                "The file should be uploaded as a multipart/form-data request with the key 'file'."
        ),
        request=inline_serializer(
            name="InlineUploadFileSerializer",
            fields={"file": serializers.FileField()},
        ),
        responses={201: ProductSerializer(many=True)},
    )
    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
        permission_classes=[IsAuthenticated, ProductPermission],
        url_path="import/tabular",
        filter_backends=[]
    )
    def import_tabular(self, request, *args, **kwargs):
        """
        Imports products from an uploaded tabular file (CSV, XLS, or XLSX).

        Args:
            request (HttpRequest): The HTTP request object containing the tabular file.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP 201 Created response with serialized new product data on success.

        Raises:
            ValidationError: If no file, more than one file, or import errors occur.
            UnsupportedMediaType: If the uploaded file has an invalid extension.
        """
        if 'file' not in request.FILES or len(request.FILES) != 1:
            raise ValidationError({"file": "Please upload exactly one file under the 'file' key."})

        uploaded = request.FILES['file']

        # Validate extension
        allowed = ['csv', 'xls', 'xlsx']
        validator = FileExtensionValidator(allowed_extensions=allowed)
        try:
            validator(uploaded)
        except ValidationError:
            raise UnsupportedMediaType("Invalid file extension. Only .csv, .xls, .xlsx is allowed.")

        # Read raw bytes and determine format
        name = uploaded.name
        ext = name.rsplit(".", 1)[1].lower()
        raw = uploaded.read()

        # Load into a Tablib Dataset
        if ext == 'csv':
            text = raw.decode('utf-8')
            dataset = Dataset().load(text, format='csv')
        else:
            fmt = 'xls' if ext == 'xls' else 'xlsx'
            dataset = Dataset().load(raw, format=fmt)

        # Perform import
        resource = ProductResource()
        result = resource.import_data(
            dataset,
            dry_run=False,
            supplier=self.get_parent_company(),
            retain_instance_in_row_result=True
        )

        # Success: serialize newly created products
        if not result.has_errors():
            created = []
            for row in result.rows:
                if row.import_type == RowResult.IMPORT_TYPE_NEW:
                    created.append(self.get_serializer(row.instance).data)
            return Response(created, status=status.HTTP_201_CREATED)

        # Failure: collect errors
        errors = []
        for err_row in result.error_rows:
            for err in err_row.errors:
                errors.append({
                    "row": err.row,
                    "error": repr(err.error),
                })
        raise ValidationError(errors)