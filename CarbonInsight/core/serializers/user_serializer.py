from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")

class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id",)


class UserUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile information"""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def validate_email(self, value):
        """Validate that the email is not already in use"""
        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def update(self, instance, validated_data):
        """Update user profile"""
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)

        # Update email if provided
        if "email" in validated_data:
            instance.email = validated_data["email"]
            # Also update username if it's the same as email (our default setup)
            if instance.username == instance.email or instance.username.startswith(
                instance.email.split("@")[0]
            ):
                instance.username = validated_data["email"]

        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        """Validate that the passwords match"""
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords don't match."}
            )
        return data


class UserPasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("old_password", "new_password", "new_password_confirm")

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect.")

        if old_password == new_password:
            raise serializers.ValidationError("New password cannot be the same as the old password.")

        if new_password != new_password_confirm:
            raise serializers.ValidationError("New passwords do not match.")

        return attrs