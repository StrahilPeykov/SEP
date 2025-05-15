from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core import serializers
from core.models import Company, CompanyMembership
from core.permissions import IsCompanyMember, CanEditCompany
from core.serializers import CompanySerializer
from core.serializers.user_serializer import UserUsernameSerializer, UserSerializer

User = get_user_model()

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, CanEditCompany]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'vat_number', 'business_registration_number']
    search_fields = ['name', 'vat_number', 'business_registration_number']

    def perform_create(self, serializer):
        company = serializer.save()
        user = self.request.user
        membership, created = CompanyMembership.objects.get_or_create(user=user, company=company)
        if created:
            membership.save()
        return company

    @extend_schema(
        tags=["Companies"],
        summary="Create a new company",
        description="Create a new company with the given name, VAT number and business registration number. "
                    "Also adds the current user as a member."
    )
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)

    @extend_schema(
        tags=["Companies"],
        summary="Retrieve all companies",
        description="Retrieve the details of all companies in the system."
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        tags=["Companies"],
        summary="Retrieve a specific company",
        description="Retrieve the details of a specific company by its ID. "
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @extend_schema(
        tags=["Companies"],
        summary="Partially update a specific company's details",
        description="Update the details of a specific company by its ID. "
                    "Only the fields that are provided in the request body will be updated. "
                    "Action is available only to company members."
    )
    def partial_update(self, *args, **kwargs):
        return super().partial_update(*args, **kwargs)

    @extend_schema(
        tags=["Companies"],
        summary="Update a specific company's details",
        description="Update the details of a specific company by its ID. "
                    "All fields will be updated with the provided values. "
                    "Action is available only to company members."
    )
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

    @extend_schema(
        tags=["Companies"],
        summary="Delete a specific company",
        description="Delete a specific company by its ID. "
                    "Action is available only to company members."
    )
    def destroy(self, *args, **kwargs):
        return super().destroy(*args, **kwargs)

class CompanyUserViewSet(
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

    def get_company(self):
        return get_object_or_404(Company, pk=self.kwargs['company_pk'])

    def get_queryset(self):
        if self.request.user.is_anonymous:
            # For unauthenticated users, return an empty queryset
            return User.objects.none()
        return self.get_company().users.all()

    @extend_schema(
        tags=["Companies"],
        summary="List all users in a company",
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        tags=["Companies"],
        summary="Add a user to a company"
    )
    def create(self, request, company_pk=None):
        try:
            user = User.objects.get(username=request.data.get('username'))
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        CompanyMembership.objects.get_or_create(user=user, company=self.get_company())
        return Response({'status': 'User added'}, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Companies"],
        summary="Remove a user from a company"
    )
    def destroy(self, request, pk=None, company_pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            membership = CompanyMembership.objects.get(user=user, company=self.get_company())
            membership.delete()
        except CompanyMembership.DoesNotExist:
            return Response({'detail': 'Membership not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    @extend_schema(
        tags=["Companies"],
        summary="List companies the current user belongs to"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)