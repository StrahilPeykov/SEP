from django.contrib import admin
from reversion.admin import VersionAdmin

from core.models import UserEnergyEmissionReference, UserEnergyEmissionReferenceFactor


class UserEnergyEmissionReferenceFactorInline(admin.TabularInline):
    model = UserEnergyEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor")
    extra = 0

@admin.register(UserEnergyEmissionReference)
class UserEnergyReferenceEmissionAdmin(VersionAdmin):
    list_display = ("name", "get_emission_total", "get_emission_trace")
    search_fields = ("name",)
    inlines = [UserEnergyEmissionReferenceFactorInline]

    def get_emission_total(self, reference:UserEnergyEmissionReference) -> float:
        return reference.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"