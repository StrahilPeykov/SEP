from django.contrib import admin
from reversion.admin import VersionAdmin

from core.models import Company, CompanyMembership, Product


class CompanyMembershipInline(admin.TabularInline):
    model = CompanyMembership
    fields = ("user", "company", "date_joined",)
    readonly_fields = ("date_joined",)
    extra = 0
    verbose_name = "Linked User"
    verbose_name_plural = "Linked Users"

class ProductInline(admin.TabularInline):
    model = Product
    fields = ("name", "manufacturer_name", "sku",)
    extra = 0
    verbose_name = "Product"
    verbose_name_plural = "Products"

@admin.register(Company)
class CompanyAdmin(VersionAdmin):
    model = Company
    list_display = ("name", "vat_number", "business_registration_number",)
    search_fields = ("name", "vat_number", "business_registration_number",)
    ordering = ("name",)
    inlines = [ProductInline,CompanyMembershipInline]
