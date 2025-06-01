from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.models import Company


class CompanySerializer(serializers.ModelSerializer):
    vat_number = serializers.CharField(
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )
    business_registration_number = serializers.CharField(
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )

    class Meta:
        model = Company
        fields = ("id", "name", "vat_number", "business_registration_number")