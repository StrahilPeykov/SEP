from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from core.models import CompanyMembership
from core.serializers.user_serializer import UserSerializer

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        # Ensure that the username is the same as the email
        serializer.save(username=self.request.user.email)

    def perform_destroy(self, instance):
        memberships = CompanyMembership.objects.filter(user=instance)
        for membership in memberships:
            membership.delete()
        instance.delete()

    @extend_schema(
        summary="Retrieve the current user's profile"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update the current user's profile"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Update the current user's profile"
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Delete the current user",
        description="Deletes the current user, removing them from all companies they are a member of.",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)