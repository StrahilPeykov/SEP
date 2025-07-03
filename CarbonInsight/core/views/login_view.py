from axes.decorators import axes_dispatch
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.views import TokenObtainPairView


# Use built-in SimpleJWT view for User login, obtaining tokens and refreshing tokens.
@extend_schema(
    #Creates the login endpoint by using built-in SimpleJWT view.
    summary="Login",
    description="Use this endpoint to log in and obtain access and refresh tokens.",
    tags=["Authentication"],
)
@method_decorator(axes_dispatch, name="dispatch")
# Adds a tracker in order to track the number of login attempts for account safety and hacking prevention.
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
