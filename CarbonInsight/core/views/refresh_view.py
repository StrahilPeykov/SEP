from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

User = get_user_model()

# Use built-in SimpleJWT view for token refresh
class RefreshView(TokenRefreshView):
    """
    Handles refreshing an access token using a valid refresh token.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Refresh access token",
        description="Use this endpoint to refresh your access token using a valid refresh token.",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        """
        Refreshes the user's access token given a valid refresh token.

        Args:
            request (HttpRequest): The HTTP request object containing the refresh token.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP 200 OK response with the new access token on success,
                      or an HTTP 401 Unauthorized response on failure.

        Raises:
            AuthenticationFailed: If the user account associated with the token is deleted or deactivated.
        """
        serializer = TokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # Check if this is a User.DoesNotExist error
            if "User matching query does not exist" in str(e):
                raise AuthenticationFailed("User account has been deleted or deactivated.")
            # Re-raise other exceptions
            raise

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
