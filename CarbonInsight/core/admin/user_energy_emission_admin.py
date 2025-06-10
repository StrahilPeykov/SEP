from django.contrib import admin

from core.models import UserEnergyEmissionReference, UserEnergyEmissionReferenceFactor


class UserEnergyEmissionReferenceFactorInline(admin.TabularInline):
    model = UserEnergyEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")
    extra = 0

@admin.register(UserEnergyEmissionReference)
class UserEnergyReferenceEmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "get_emission_total", "get_emission_trace",
                    "get_emission_total_non_biogenic", "get_emission_total_biogenic")
    search_fields = ("name",)
    inlines = [UserEnergyEmissionReferenceFactorInline]

    def get_emission_total(self, reference:UserEnergyEmissionReference) -> float:
        return reference.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"

    def get_emission_total_non_biogenic(self, emission: UserEnergyEmissionReference) -> float:
        return emission.get_emission_trace().total_non_biogenic

    get_emission_total_non_biogenic.short_description = "Total non-biogenic emissions"

    def get_emission_total_biogenic(self, emission: UserEnergyEmissionReference) -> float:
        return emission.get_emission_trace().total_biogenic

    get_emission_total_biogenic.short_description = "Total biogenic emissions"