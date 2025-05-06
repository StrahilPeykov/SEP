from rest_framework import serializers
from core.models import Company
from .user_serializer import UserSerializer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name", "vat_number", "business_registration_number")
