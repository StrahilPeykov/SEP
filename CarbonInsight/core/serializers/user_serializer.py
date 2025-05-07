from rest_framework import serializers
from core.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as PasswordValidationError


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
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        if old_password == new_password:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as the old password."})

        if new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password_confirm": "New password and confirm password do not match."})

        # Use Django's built-in password validation
        try:
            validate_password(new_password, user)
        except PasswordValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs