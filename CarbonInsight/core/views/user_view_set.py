from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.serializers import UserSerializer
from core.serializers.user_serializer import UserUpdateSerializer
from core.permissions import IsUserOrReadOnly

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Custom permissions:
        - List/retrieve: Authenticated users
        - Update/partial_update/destroy: Only the user themselves
        """
        if self.action in [
            "update",
            "partial_update",
            "destroy",
            "me",
            "update_profile",
            "change_password",
        ]:
            return [permissions.IsAuthenticated(), IsUserOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "update_profile":
            return UserUpdateSerializer
        return super().get_serializer_class()

    @extend_schema(
        summary="Get current user profile",
        description="Returns the profile of the authenticated user.",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Not authenticated"),
        },
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get the current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update user profile",
        description="Update the profile information of the authenticated user.",
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Not authenticated"),
        },
    )
    @action(detail=True, methods=["patch"])
    def update_profile(self, request, pk=None):
        """Update user profile data"""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Change user password",
        description="Change the password of the authenticated user.",
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Not authenticated"),
        },
    )
    @action(detail=True, methods=["post"])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response(
                {"current_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response({"status": "password changed"})

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to properly handle user deletion
        """
        instance = self.get_object()
        if instance == request.user:
            # For security, deactivate user instead of complete deletion
            instance.is_active = False
            instance.save()

            # We could do soft deletion - mark as inactive, anonymize personal data
            # This way we still preserve company relations

            return Response(
                {"detail": "Your account has been deactivated successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "You can only delete your own account."},
                status=status.HTTP_403_FORBIDDEN,
            )
