from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


# Use built-in SimpleJWT view for login
@extend_schema(
    summary="Login",
    description="Use this endpoint to log in and obtain access and refresh tokens.",
    tags=["Authentication"],
)
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
