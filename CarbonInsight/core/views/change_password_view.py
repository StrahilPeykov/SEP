from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.serializers.user_serializer import UserPasswordSerializer

class ChangePasswordView(APIView):
    """
    Handles requests for an authenticated user to update their account password.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserPasswordSerializer

    @extend_schema(
        tags=["User profile"],
        summary="Change the current user's password",
        description="Changes the password of the current user. "
                    "The old password must be provided for verification, "
                    "and the new password must be provided twice for confirmation. "
                    "All of the user's tokens will be invalidated after the password change.",
        request=UserPasswordSerializer
    )
    def post(self, request):
        """
        Processes the request to change the current user's password after validating the provided data.

        Args:
            request (HttpRequest): The HTTP request containing the old and new password details.

        Returns:
            Response: An HTTP 200 OK response on success, or a 400 Bad Request for validation errors.
        """
        serializer = UserPasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(status=HTTP_200_OK)