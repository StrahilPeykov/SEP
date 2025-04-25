from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username','email','password')

    def create(self, validated):
        user = User.objects.create_user(
            username=validated['username'],
            email=validated.get('email'),
            password=validated['password']
        )
        return user