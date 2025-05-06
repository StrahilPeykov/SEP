from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from core.models import CompanyMembership


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "date_joined")
    list_filter = (
        ("user", RelatedDropdownFilter),
        ("company", RelatedDropdownFilter),
    )
    search_fields = (
        "company__name",
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    ordering = ("company", "user", "date_joined")