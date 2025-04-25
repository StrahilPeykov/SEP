from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView


# Use built-in SimpleJWT view for token refresh
class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]