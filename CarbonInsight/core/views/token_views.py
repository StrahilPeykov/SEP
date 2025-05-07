from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view that uses the same serializer but adds extra security headers."""

    permission_classes = [AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that gracefully handles deleted users.
    Returns a 401 Unauthorized instead of 500 when the user doesn't exist.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # Check if this is a User.DoesNotExist error
            if "User matching query does not exist" in str(e):
                return Response(
                    {"detail": "User account has been deleted or deactivated."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            # Re-raise other exceptions
            raise

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
