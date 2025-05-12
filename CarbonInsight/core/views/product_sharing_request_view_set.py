from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Company, ProductSharingRequest, ProductSharingRequestStatus
from core.permissions import IsCompanyMember
from core.serializers.product_sharing_request_serializer import ProductSharingRequestSerializer
from core.serializers.bulk_action_serializer import BulkActionSerializer


class ProductSharingRequestViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSharingRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_serializer_class(self):
        if self.action in ["bulk_approve", "bulk_deny"]:
            return BulkActionSerializer
        return super().get_serializer_class()

    def get_parent_company(self):
        return Company.objects.get(pk=self.kwargs['company_pk'])

    def get_queryset(self):
        company = self.get_parent_company()
        return ProductSharingRequest.objects.filter(
            product__supplier=company
        )

    def check_permissions(self, request):
        # First enforce IsAuthenticated
        super().check_permissions(request)

        # Then enforce company membership
        company = self.get_parent_company()
        if not company.user_is_member(request.user):
            self.permission_denied(
                request,
                message='You are not a member of this company.'
            )

    @extend_schema(
        tags=["Product sharing requests"],
        summary="Retrieve all product sharing requests",
        description=(
            "Retrieve the details of all product sharing requests for the company with `company_pk`."
        ),
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        tags=["Product sharing requests"],
        summary="Approve product sharing requests",
        description=(
            "Approve the product sharing requests with the given IDs. "
            "The requests will be marked as accepted."
        ),
    )
    @action(detail=False, methods=["post"])
    def bulk_approve(self, request, company_pk=None):
        qs = self.get_queryset().filter(id__in=request.data.get("ids"))
        updated = qs.update(status=ProductSharingRequestStatus.ACCEPTED)
        return Response({"updated": updated}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Product sharing requests"],
        summary="Deny product sharing requests",
        description=(
            "Deny the product sharing requests with the given IDs. "
            "The requests will be marked as rejected."
        ),
    )
    @action(detail=False, methods=["post"])
    def bulk_deny(self, request, company_pk=None):
        qs = self.get_queryset().filter(id__in=request.data.get("ids"))
        updated = qs.update(status=ProductSharingRequestStatus.REJECTED)
        return Response({"updated": updated}, status=status.HTTP_200_OK)