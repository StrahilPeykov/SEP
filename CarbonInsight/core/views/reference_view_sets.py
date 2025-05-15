from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated

from core.models.transport_emission import TransportEmissionReference
from core.serializers.reference_view_sets import MaterialEmissionReferenceSerializer, \
    ProductionEnergyEmissionReferenceSerializer, \
    UserEnergyEmissionReferenceSerializer, TransportEmissionReferenceSerializer
from core.models import UserEnergyEmissionReference, ProductionEnergyEmissionReference, MaterialEmissionReference


class TransportEmissionReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransportEmissionReference.objects.all()
    serializer_class = TransportEmissionReferenceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reference"],
        summary="Retrieve all transport emission references",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Reference"],
        summary="Retrieve a specific transport emission reference",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class UserEnergyEmissionReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserEnergyEmissionReference.objects.all()
    serializer_class = UserEnergyEmissionReferenceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reference"],
        summary="Retrieve all user energy emission references",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Reference"],
        summary="Retrieve a specific user energy emission reference",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class ProductionEnergyEmissionReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductionEnergyEmissionReference.objects.all()
    serializer_class = ProductionEnergyEmissionReferenceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reference"],
        summary="Retrieve all production energy emission references",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Reference"],
        summary="Retrieve a specific production energy emission reference",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class MaterialEmissionReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaterialEmissionReference.objects.all()
    serializer_class = MaterialEmissionReferenceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reference"],
        summary="Retrieve all material emission references",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Reference"],
        summary="Retrieve a specific material emission reference",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
