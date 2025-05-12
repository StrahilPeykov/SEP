from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as PasswordValidationError

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password", "confirm_password")

    def validate(self, attrs):
        # Check if passwords match
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({
                "password": "Password and confirm password do not match.",
                "confirm_password": "Password and confirm password do not match."
            })
        
        # Validate password strength
        try:
            # We pass None as the user since we don't have a user instance yet
            validate_password(attrs.get("password"))
        except PasswordValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
            
        return attrs

    def create(self, validated_data):
        # Remove confirm_password from validated data
        validated_data.pop("confirm_password", None)
        
        user = User.objects.create_user(
            username=validated_data.get("email"),
            email=validated_data.get("email"),
            password=validated_data.get("password"),
        )
        user.first_name = validated_data.get("first_name")
        user.last_name = validated_data.get("last_name")
        user.save()
        return user
