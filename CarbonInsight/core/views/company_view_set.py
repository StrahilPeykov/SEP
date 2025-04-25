from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Company, CompanyMembership
from core.serializers import CompanySerializer

User = get_user_model()

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(detail=True, methods=['post'])
    def add_user(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail':'User not found'}, status=404)
        CompanyMembership.objects.get_or_create(user=user, company=company)
        return Response({'status':'user added'})