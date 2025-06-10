from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelFilter, PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from core.models import Emission, ProductionEnergyEmission, TransportEmission, UserEnergyEmission, \
    EmissionBoMLink, EmissionOverrideFactor


class EmissionOverrideFactorInline(admin.TabularInline):
    model = EmissionOverrideFactor
    fields = ("lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")
    extra = 0

class EmissionBoMLinkAdminInline(admin.TabularInline):
    model = EmissionBoMLink
    fields = ("line_item",)
    extra = 0
    verbose_name = "BoM line item link"
    verbose_name_plural = "BoM line item links"

@admin.register(Emission)
class EmissionAdmin(PolymorphicParentModelAdmin):
    base_model = Emission  # Optional, explicitly set here.
    child_models = (ProductionEnergyEmission, TransportEmission, UserEnergyEmission)
    list_display = ("parent_product", "get_emission_total", "get_emission_total_biogenic",
                    "get_emission_total_non_biogenic", "pcf_calculation_method")
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
    inlines = [EmissionBoMLinkAdminInline, EmissionOverrideFactorInline]

    def get_emission_total(self, emission:Emission) -> float:
        return emission.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"

    def get_emission_total_non_biogenic(self, emission:Emission) -> float:
        return emission.get_emission_trace().total_non_biogenic
    get_emission_total_non_biogenic.short_description = "Total non-biogenic emissions"

    def get_emission_total_biogenic(self, emission:Emission) -> float:
        return emission.get_emission_trace().total_biogenic
    get_emission_total_biogenic.short_description = "Total biogenic emissions"


class EmissionChildAdmin(PolymorphicChildModelAdmin):
    base_model = Emission  # Optional, explicitly set here.
    inlines = [EmissionBoMLinkAdminInline, EmissionOverrideFactorInline]

    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.

    def get_emission_total(self, emission:Emission) -> float:
        return emission.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"

    def get_emission_total_non_biogenic(self, emission:Emission) -> float:
        return emission.get_emission_trace().total_non_biogenic
    get_emission_total_non_biogenic.short_description = "Total non-biogenic emissions"

    def get_emission_total_biogenic(self, emission:Emission) -> float:
        return emission.get_emission_trace().total_biogenic
    get_emission_total_biogenic.short_description = "Total biogenic emissions"

@admin.register(ProductionEnergyEmission)
class ProductionEnergyEmissionAdmin(EmissionChildAdmin):
    base_model = ProductionEnergyEmission
    list_display = EmissionAdmin.list_display + ("energy_consumption", "reference")
    list_filter = ("reference",)
    show_in_index = True

@admin.register(TransportEmission)
class TransportEmissionAdmin(EmissionChildAdmin):
    base_model = TransportEmission
    list_display = EmissionAdmin.list_display + ("distance", "weight", "reference")
    list_filter = ("reference",)
    show_in_index = True

@admin.register(UserEnergyEmission)
class UserEnergyEmissionAdmin(EmissionChildAdmin):
    base_model = UserEnergyEmission
    list_display = EmissionAdmin.list_display + ("energy_consumption", "reference")
    list_filter = ("reference",)
    show_in_index = True