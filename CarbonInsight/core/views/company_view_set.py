from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
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

    def get_serializer_class(self):
        if self.action in ["add_user", "remove_user"]:
            return UserUsernameSerializer
        if self.action in ["list_users"]:
            return UserSerializer
        return super().get_serializer_class()

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

    @extend_schema(
        tags=["Companies"],
        summary="Add a user to a company"
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsCompanyMember])
    def add_user(self, request, pk=None):
        company = self.get_object()
        try:
            user = User.objects.get(username=request.data.get("username"))
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
        CompanyMembership.objects.get_or_create(user=user, company=company)
        return Response({"status": "User added"}, status=201)

    @extend_schema(
        tags=["Companies"],
        summary="List all users in a company",
    )
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsCompanyMember])
    def list_users(self, request, pk=None):
        company = self.get_object()
        users = company.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Companies"],
        summary="Remove a user from a company"
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsCompanyMember])
    def remove_user(self, request, pk=None):
        company = self.get_object()
        try:
            user = User.objects.get(username=request.data.get("username"))
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
        try:
            membership = CompanyMembership.objects.get(user=user, company=company)
            membership.delete()
        except CompanyMembership.DoesNotExist:
            return Response({"detail": "Membership not found"}, status=404)
        return Response({"status": "User removed"})

    @extend_schema(
        tags=["Companies"],
        summary="List companies the current user belongs to"
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def my(self, request):
        queryset = request.user.companies.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)