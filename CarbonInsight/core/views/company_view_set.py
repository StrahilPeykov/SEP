from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
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

    def get_serializer_class(self):
        if self.action in ["add_user", "remove_user"]:
            return UserUsernameSerializer
        if self.action in ["list_users"]:
            return UserSerializer
        return super().get_serializer_class()

    @extend_schema(
        summary="Create a new company",
        description="Create a new company with the given name, VAT number and business registration number. "
                    "Also adds the current user as a member."
    )
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)

    @extend_schema(
        summary="Retrieve all companies",
        description="Retrieve the details of all companies in the system."
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        summary="Retrieve a specific company",
        description="Retrieve the details of a specific company by its ID. "
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @extend_schema(
        summary="Partially update a specific company's details",
        description="Update the details of a specific company by its ID. "
                    "Only the fields that are provided in the request body will be updated. "
                    "Action is available only to company members."
    )
    def partial_update(self, *args, **kwargs):
        return super().partial_update(*args, **kwargs)

    @extend_schema(
        summary="Update a specific company's details",
        description="Update the details of a specific company by its ID. "
                    "All fields will be updated with the provided values. "
                    "Action is available only to company members."
    )
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

    @extend_schema(
        summary="Delete a specific company",
        description="Delete a specific company by its ID. "
                    "Action is available only to company members."
    )
    def destroy(self, *args, **kwargs):
        return super().destroy(*args, **kwargs)

    @extend_schema(
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
        summary="List all users in a company",
    )
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsCompanyMember])
    def list_users(self, request, pk=None):
        company = self.get_object()
        users = company.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @extend_schema(
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