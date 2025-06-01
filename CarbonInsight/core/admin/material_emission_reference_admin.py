from django.contrib import admin
from reversion.admin import VersionAdmin

from core.models import MaterialEmissionReference, MaterialEmissionReferenceFactor


class MaterialEmissionReferenceFactorInline(admin.TabularInline):
    model = MaterialEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")
    extra = 0

@admin.register(MaterialEmissionReference)
class MaterialReferenceEmissionAdmin(VersionAdmin):
    list_display = ("name", "get_emission_total", "get_emission_trace",
                    "get_emission_total_non_biogenic", "get_emission_total_biogenic")
    search_fields = ("name",)
    inlines = [MaterialEmissionReferenceFactorInline]

    def get_emission_total(self, emission: MaterialEmissionReference) -> float:
        return emission.get_emission_trace().total

    get_emission_total.short_description = "Total emissions"

    def get_emission_total_non_biogenic(self, emission: MaterialEmissionReference) -> float:
        return emission.get_emission_trace().total_non_biogenic

    get_emission_total_non_biogenic.short_description = "Total non-biogenic emissions"

    def get_emission_total_biogenic(self, emission: MaterialEmissionReference) -> float:
        return emission.get_emission_trace().total_biogenic

    get_emission_total_biogenic.short_description = "Total biogenic emissions"