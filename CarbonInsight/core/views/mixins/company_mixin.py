from typing import TypeVar

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ModelViewSet

from core.models import Company

T = TypeVar('T', bound=ModelViewSet)

def resolve_company_pk(company_pk: str) -> int:
    """
    Resolves the company_pk from the URL, handling the special case
    for the reference company.
    """
    if company_pk == "reference":
        return Company.objects.get(is_reference=True).pk
    return int(company_pk)

class CompanyMixin:
    """
    Provides `get_parent_company()` for viewsets whose URL includes
    a `company_pk` kwarg.
    """
    def get_parent_company(self:T):
        if 'company_pk' not in self.kwargs:
            return NotFound("Company not specified in URL.")
        return get_object_or_404(
            Company,
            pk=resolve_company_pk(self.kwargs.get('company_pk'))
        )

    def get_parent_company_pk(self:T):
        return self.get_parent_company().pk