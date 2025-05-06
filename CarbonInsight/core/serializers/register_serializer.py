from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password", "confirm_password")

    def create(self, validated):
        if validated.get("password") != validated.get("confirm_password"):
            raise serializers.ValidationError({
                "password": "Password and confirm password do not match.",
                "confirm_password": "Password and confirm password do not match."
            })

        user = User.objects.create_user(
            username=validated.get("email"),
            email=validated.get("email"),
            password=validated.get("password"),
        )
        user.first_name = validated.get("first_name")
        user.last_name = validated.get("last_name")
        user.save()
        return user
