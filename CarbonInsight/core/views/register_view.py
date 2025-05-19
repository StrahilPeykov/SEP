from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from core.serializers import RegisterSerializer, UserSerializer

User = get_user_model()

@extend_schema_view(
    create=extend_schema(
        tags=["Authentication"],
        summary="Register a new user",
        description="Creates a new user and returns the user data along with access and refresh tokens.",
    ),
)
class RegisterView(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        token = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(token.access_token),
                "refresh": str(token),
            },
            status=status.HTTP_201_CREATED,
        )
