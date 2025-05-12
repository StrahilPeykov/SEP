from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from reversion.admin import VersionAdmin

from core.models import Product, ProductSharingRequest

class ProductSharingRequestInline(admin.TabularInline):
    model = ProductSharingRequest
    extra = 0
    fields = ("requester", "status", "created_at")
    readonly_fields = ("created_at",)

@admin.register(Product)
class ProductAdmin(VersionAdmin):
    model = Product
    list_display = ("name", "supplier", "manufacturer", "sku",)
    search_fields = ("name", "supplier__name", "manufacturer", "sku",)
    ordering = ("name",)
    list_filter = (
        ("supplier", RelatedDropdownFilter),
        ("is_public", admin.BooleanFieldListFilter),
    )
    inlines = [ProductSharingRequestInline]