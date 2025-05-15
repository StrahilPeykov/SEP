from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelFilter, PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from reversion.admin import VersionAdmin

from core.models import Emission, MaterialEmission, ProductionEnergyEmission, TransportEmission, UserEnergyEmission, \
    EmissionBoMLink


class EmissionBoMLinkAdminInline(admin.TabularInline):
    model = EmissionBoMLink
    fields = ("line_item",)
    extra = 0
    verbose_name = "BoM line item link"
    verbose_name_plural = "BoM line item links"

@admin.register(Emission)
class EmissionAdmin(VersionAdmin, PolymorphicParentModelAdmin):
    base_model = Emission  # Optional, explicitly set here.
    child_models = (MaterialEmission, ProductionEnergyEmission, TransportEmission, UserEnergyEmission)
    list_display = ("parent_product", "get_emission_total", "get_emission_trace")
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
    inlines = [EmissionBoMLinkAdminInline]

    def get_emission_total(self, emission:Emission) -> float:
        return emission.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"


class EmissionChildAdmin(PolymorphicChildModelAdmin):
    base_model = Emission  # Optional, explicitly set here.
    inlines = [EmissionBoMLinkAdminInline]

    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.

    def get_emission_total(self, emission:Emission) -> float:
        return emission.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"

@admin.register(MaterialEmission)
class MaterialEmissionAdmin(VersionAdmin, EmissionChildAdmin):
    base_model = MaterialEmission
    list_display = EmissionAdmin.list_display + ("weight", "reference")
    list_filter = ("reference",)
    show_in_index = True

@admin.register(ProductionEnergyEmission)
class ProductionEnergyEmissionAdmin(VersionAdmin, EmissionChildAdmin):
    base_model = ProductionEnergyEmission
    list_display = EmissionAdmin.list_display + ("energy_consumption", "reference")
    list_filter = ("reference",)
    show_in_index = True

@admin.register(TransportEmission)
class TransportEmissionAdmin(VersionAdmin, EmissionChildAdmin):
    base_model = TransportEmission
    list_display = EmissionAdmin.list_display + ("distance", "weight", "reference")
    list_filter = ("reference",)
    show_in_index = True

@admin.register(UserEnergyEmission)
class UserEnergyEmissionAdmin(VersionAdmin, EmissionChildAdmin):
    base_model = UserEnergyEmission
    list_display = EmissionAdmin.list_display + ("energy_consumption", "reference")
    list_filter = ("reference",)
    show_in_index = True