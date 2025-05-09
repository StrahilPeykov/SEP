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

    def perform_destroy(self, instance):
        memberships = CompanyMembership.objects.filter(user=instance)
        for membership in memberships:
            membership.delete()
        instance.delete()

    @extend_schema(
        tags=["User profile"],
        summary="Retrieve the current user's profile"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["User profile"],
        summary="Partially update the current user's profile"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["User profile"],
        summary="Update the current user's profile"
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["User profile"],
        summary="Delete the current user",
        description="Deletes the current user, removing them from all companies they are a member of.",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)