from rest_framework import serializers
from core.models import Company
from .user_serializer import UserSerializer


class CompanySerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Company
        fields = ('id','name','users')