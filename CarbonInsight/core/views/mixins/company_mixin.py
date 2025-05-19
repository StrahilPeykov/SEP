from typing import TypeVar

from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from core.models import Company

T = TypeVar('T', bound=ModelViewSet)

class CompanyMixin:
    """
    Provides `get_parent_company()` for viewsets whose URL includes
    a `company_pk` kwarg.
    """
    def get_parent_company(self:T):
        return get_object_or_404(
            Company,
            pk=self.kwargs['company_pk']
        )