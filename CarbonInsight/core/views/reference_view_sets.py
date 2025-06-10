from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated

from core.models.transport_emission import TransportEmissionReference
from core.serializers.reference_serializers import \
    ProductionEnergyEmissionReferenceSerializer, \
    UserEnergyEmissionReferenceSerializer, TransportEmissionReferenceSerializer
from core.models import UserEnergyEmissionReference, ProductionEnergyEmissionReference

@extend_schema_view(
    list=extend_schema(
        tags=["Reference"],
        summary="Retrieve all transport emission references",
        description="Retrieve a list of all transport emission references.",
    ),
    retrieve=extend_schema(
        tags=["Reference"],
        summary="Retrieve a specific transport emission reference",
        description="Retrieve the details of a specific transport emission reference by its ID.",
    ),
)
class TransportEmissionReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransportEmissionReference.objects.all()
    serializer_class = TransportEmissionReferenceSerializer
    permission_classes = [IsAuthenticated]

@extend_schema_view(
    list=extend_schema(
        tags=["Reference"],
        summary="Retrieve all user energy emission references",
        description="Retrieve a list of all user energy emission references.",
    ),
    retrieve=extend_schema(
        tags=["Reference"],
        summary="Retrieve a specific user energy emission reference",
        description="Retrieve the details of a specific user energy emission reference by its ID.",
    ),
)
class UserEnergyEmissionReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserEnergyEmissionReference.objects.all()
    serializer_class = UserEnergyEmissionReferenceSerializer
    permission_classes = [IsAuthenticated]

@extend_schema_view(
    list=extend_schema(
        tags=["Reference"],
        summary="Retrieve all production energy emission references",
        description="Retrieve a list of all production energy emission references.",
    ),
    retrieve=extend_schema(
        tags=["Reference"],
        summary="Retrieve a specific production energy emission reference",
        description="Retrieve the details of a specific production energy emission reference by its ID.",
    ),
)
class ProductionEnergyEmissionReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductionEnergyEmissionReference.objects.all()
    serializer_class = ProductionEnergyEmissionReferenceSerializer
    permission_classes = [IsAuthenticated]

