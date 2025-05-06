from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from reversion.admin import VersionAdmin

from core.models import Product

class ProductAdmin(VersionAdmin):
    model = Product
    list_display = ("name", "company", "manufacturer", "sku",)
    search_fields = ("name", "company__name", "manufacturer", "sku",)
    ordering = ("name",)
    list_filter = (
        ("company", RelatedDropdownFilter),
    )