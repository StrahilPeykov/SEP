from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.models import Company


class CompanyListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing companies with basic details.
    """
    vat_number = serializers.CharField(
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )
    business_registration_number = serializers.CharField(
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )

    class Meta:
        model = Company
        fields = ("id", "name", "vat_number", "business_registration_number", "auto_approve_product_sharing_requests")

class CompanyDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for a detailed view of a company, including additional metrics.
    Use this sparely because of costly database queries.
    """

    class Meta:
        model = Company
        fields = CompanyListSerializer.Meta.fields + (
            "companies_using_count",
            "products_using_count",
            "total_emissions_across_products",
        )
        read_only_fields = (
            "companies_using_count",
            "products_using_count",
            "total_emissions_across_products",
        )
