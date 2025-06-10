from auditlog.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Company, CompanyMembership, Product
from core.permissions import IsCompanyMember, CanEditCompany
from core.serializers.audit_log_entry_serializer import AuditLogEntrySerializer
from core.serializers.company_serializer import CompanySerializer
from core.serializers.user_serializer import UserUsernameSerializer, UserSerializer
from core.views.mixins.company_mixin import CompanyMixin

User = get_user_model()


@extend_schema_view(
    create=extend_schema(
        tags=["Companies"],
        summary="Create a new company",
        description="Create a new company with the given name, VAT number and business registration number. "
                    "Also adds the current user as a member.",
    ),
    list=extend_schema(
        tags=["Companies"],
        summary="Retrieve all companies",
        description="Retrieve the details of all companies in the system.",
    ),
    retrieve=extend_schema(
        tags=["Companies"],
        summary="Retrieve a specific company",
        description="Retrieve the details of a specific company by its ID.",
    ),
    partial_update=extend_schema(
        tags=["Companies"],
        summary="Partially update a specific company's details",
        description="Update the details of a specific company by its ID. "
                    "Only the fields that are provided in the request body will be updated."
                    "Action is available only to company members.",
    ),
    update=extend_schema(
        tags=["Companies"],
        summary="Update a specific company's details",
        description="Update the details of a specific company by its ID. "
                    "All fields will be updated with the provided values. "
                    "Action is available only to company members.",
    ),
    destroy=extend_schema(
        tags=["Companies"],
        summary="Delete a specific company",
        description="Delete a specific company by its ID. "
                    "Action is available only to company members.",
    ),
)
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(is_reference=False)
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, CanEditCompany]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'vat_number', 'business_registration_number']
    search_fields = ['name', 'vat_number', 'business_registration_number']

    def get_serializer_class(self):
        if self.action in ['audit']:
            return AuditLogEntrySerializer
        return super().get_serializer_class()

    def get_object(self):
        raw_pk = self.kwargs["pk"]
        if raw_pk == "reference":
            # Look up the one reference company
            try:
                company = Company.objects.get(is_reference=True)
            except Company.DoesNotExist:
                raise NotFound("No reference company defined.")
            return company
        # Otherwise, fall back to normal queryset lookup
        return super().get_object()

    def perform_create(self, serializer):
        company = serializer.save()
        user = self.request.user
        membership, created = CompanyMembership.objects.get_or_create(user=user, company=company)
        if created:
            membership.save()
        return company

    @extend_schema(
        tags=["Companies"],
        summary="Audit log for company",
        description="Retrieve the audit log entries for a specific company and its products. ",
        responses=AuditLogEntrySerializer(many=True),
    )
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, CanEditCompany], url_path="audit")
    def audit(self, request, *args, **kwargs):
        company = self.get_object()

        # 1. Company itself
        base_q = Q(
            content_type=ContentType.objects.get_for_model(company),
            object_pk__in=[company.pk],
        )

        # 2. Product logs
        base_q |= Q(
            content_type=ContentType.objects.get_for_model(Product),
            object_pk__in=Product.objects.filter(supplier=company).values_list('pk', flat=True),
        )

        logs = LogEntry.objects.filter(base_q).order_by("-timestamp")

        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    parameters=[
        OpenApiParameter(
            name="company_pk",
            type=int,
            location="path",
            description="Primary key of the parent Company",
        ),
    ]
)
@extend_schema_view(
    list=extend_schema(
        tags=["Companies"],
        summary="List all users in a company",
        description="Retrieve the details of all users in a specific company.",
    ),
    create=extend_schema(
        tags=["Companies"],
        summary="Add a user to a company",
        description="Add a user to a specific company by their username.",
    ),
    destroy=extend_schema(
        tags=["Companies"],
        summary="Remove a user from a company",
        description="Remove a user from a specific company by their ID.",
    ),
)
class CompanyUserViewSet(
    CompanyMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserUsernameSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_serializer_class(self):
        if self.action == "list":
            return UserSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_anonymous:
            # For unauthenticated users, return an empty queryset
            return User.objects.none()
        return self.get_parent_company().users.all()

    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username=request.data.get('username'))
        except User.DoesNotExist:
            raise NotFound("User with this username does not exist.")
        CompanyMembership.objects.get_or_create(user=user, company=self.get_parent_company())
        LogEntry.objects.log_create(instance=self.get_parent_company(), force_log=True, action=LogEntry.Action.CREATE,
                                    changes_text=f"Added user {user.username} to company.")
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, company_pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User with this ID does not exist.")
        try:
            membership = CompanyMembership.objects.get(user=user, company=self.get_parent_company())
            membership.delete()
        except CompanyMembership.DoesNotExist:
            raise NotFound("User is not a member of this company.")
        LogEntry.objects.log_create(instance=self.get_parent_company(), force_log=True, action=LogEntry.Action.DELETE,
                                    changes_text=f"Removed user {user.username} from company.")
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema_view(
    list=extend_schema(
        tags=["Companies"],
        summary="List companies the current user belongs to",
        description="Retrieve the details of all companies the current user belongs to.",
    ),
)
class MyCompaniesViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["name", "vat_number", "business_registration_number"]
    search_fields = ["name", "vat_number", "business_registration_number"]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            # This if is needed for the schema generation
            return Company.objects.none()
        # Return only companies for the current user
        return self.request.user.companies.all()