from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from reversion.admin import VersionAdmin

from core.models import Product, ProductSharingRequest, ProductBoMLineItem, Emission



class ProductBoMLineItemInline(admin.TabularInline):
    model = ProductBoMLineItem
    fk_name = "parent_product"
    fields = ("line_item_product", "quantity",)
    extra = 0
    verbose_name = "BoM line item"
    verbose_name_plural = "BoM line items"

class ProductBoMLineItemUsedInInline(admin.TabularInline):
    model = ProductBoMLineItem
    fk_name = "line_item_product"
    fields = ("parent_product", "quantity",)
    readonly_fields = ("parent_product", "quantity",)
    extra = 0
    can_delete = False
    show_change_link = False
    verbose_name = "Used in"
    verbose_name_plural = "Used in"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class ProductSharingRequestInline(admin.TabularInline):
    model = ProductSharingRequest
    extra = 0
    fields = ("requester", "status", "created_at")
    readonly_fields = ("created_at",)

@admin.register(Product)
class ProductAdmin(VersionAdmin):
    model = Product
    list_display = ("name", "supplier", "manufacturer_name", "sku", "get_emission_total", "get_emission_trace")
    search_fields = ("name", "supplier__name", "manufacturer_name", "sku",)
    ordering = ("name",)
    list_filter = (
        ("supplier", RelatedDropdownFilter),
        ("is_public", admin.BooleanFieldListFilter),
    )
    inlines = [ProductSharingRequestInline, ProductBoMLineItemInline, ProductBoMLineItemUsedInInline]

    def get_emission_total(self, product:Product) -> float:
        return product.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"