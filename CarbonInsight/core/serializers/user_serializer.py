from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")

class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id",)

class UserUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)