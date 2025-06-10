from django.contrib import admin

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
    can_delete = False
    show_change_link = False
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display = ("name", "vat_number", "business_registration_number", "is_reference", "auto_approve_product_sharing_requests")
    search_fields = ("name", "vat_number", "business_registration_number", "is_reference", "auto_approve_product_sharing_requests")
    ordering = ("name",)
    inlines = [ProductInline,CompanyMembershipInline]
    list_filter = (
        ("is_reference", admin.BooleanFieldListFilter),
        ("auto_approve_product_sharing_requests", admin.BooleanFieldListFilter),
    )
