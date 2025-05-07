from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.serializers import UserSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Return the authenticated user's profile information.
    This endpoint is used to verify authentication and get user details.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
