from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


# Use built-in SimpleJWT view for login
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
