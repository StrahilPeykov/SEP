from typing import Optional

from django.contrib import admin
from django.http import HttpRequest

from core.models import Company, CompanyMembership, Product


class CompanyMembershipInline(admin.TabularInline):
    """
    Defines the CompanyMembership fields to be presented inline when editing a Company.
    """

    model = CompanyMembership
    fields = ("user", "company", "date_joined",)
    readonly_fields = ("date_joined",)
    extra = 0
    verbose_name = "Linked User"
    verbose_name_plural = "Linked Users"

class ProductInline(admin.TabularInline):
    """
    Defines the Product fields to be presented inline when editing a Company.
    """

    model = Product
    fields = ("name", "manufacturer_name", "sku",)
    extra = 0
    verbose_name = "Product"
    verbose_name_plural = "Products"
    can_delete = False
    show_change_link = False
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj:Optional[Product]=None) -> bool:
        """
        Forces everything to be read-only
        """
        return False

    def has_delete_permission(self, request: HttpRequest, obj:Optional[Product]=None) -> bool:
        """
        Forces everything to be read-only
        """
        return False

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Defines the fields to be presented and how they are shown in the admin panel for Company.
    """

    model = Company
    list_display = ("name", "vat_number", "business_registration_number", "is_reference", "auto_approve_product_sharing_requests")
    search_fields = ("name", "vat_number", "business_registration_number", "is_reference", "auto_approve_product_sharing_requests")
    ordering = ("name",)
    inlines = [ProductInline,CompanyMembershipInline]
    list_filter = (
        ("is_reference", admin.BooleanFieldListFilter),
        ("auto_approve_product_sharing_requests", admin.BooleanFieldListFilter),
    )
