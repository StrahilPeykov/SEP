from typing import TypeVar

from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from core.models import Product

T = TypeVar('T', bound=ModelViewSet)

class ProductMixin:
    """
    Provides `get_parent_product()` for viewsets whose URL includes
    a `product_pk` kwarg.  Depends on CompanyMixin to resolve the supplier.
    """
    def get_parent_product(self:T):
        return get_object_or_404(
            Product,
            pk=self.kwargs['product_pk'],
            supplier=self.get_parent_company()
        )