from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics

from core.models import CompanyMembership
from core.serializers.user_serializer import UserSerializer

User = get_user_model()

@extend_schema_view(
    get=extend_schema(
        tags=["User profile"],
        summary="Retrieve the current user's profile",
        description="Retrieve the details of the currently authenticated user.",
    ),
    patch=extend_schema(
        tags=["User profile"],
        summary="Partially update the current user's profile",
        description="Update specific fields of the currently authenticated user's profile.",
    ),
    put=extend_schema(
        tags=["User profile"],
        summary="Update the current user's profile",
        description="Update the entire profile of the currently authenticated user.",
    ),
    delete=extend_schema(
        tags=["User profile"],
        summary="Delete the current user",
        description="Delete the currently authenticated user and remove them from all companies they are a member of.",
    ),
)
class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting the currently authenticated user's profile.
    """
    serializer_class = UserSerializer

    def get_object(self):
        """
        Retrieves the currently authenticated user.

        Returns:
            User: The currently authenticated user instance.
        """
        return self.request.user

    def perform_destroy(self, instance):
        """
        Performs the deletion of the user instance and their associated company memberships.

        Args:
            instance (User): The user instance to be deleted.
        """
        memberships = CompanyMembership.objects.filter(user=instance)
        for membership in memberships:
            membership.delete()
        instance.delete()