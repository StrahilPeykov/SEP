from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelFilter, PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from reversion.admin import VersionAdmin

from core.models import Emission, EndOfLifeEmission, MaterialEmission, ProductionEnergyEmission, TransportEmission, UserEnergyEmission

@admin.register(Emission)
class EmissionAdmin(VersionAdmin, PolymorphicParentModelAdmin):
    base_model = Emission  # Optional, explicitly set here.
    child_models = (EndOfLifeEmission, MaterialEmission, ProductionEnergyEmission, TransportEmission, UserEnergyEmission)
    list_display = ("content_object", "calculate_emissions")
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.


class EmissionChildAdmin(PolymorphicChildModelAdmin):
    base_model = Emission  # Optional, explicitly set here.

    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.

@admin.register(EndOfLifeEmission)
class EndOfLifeEmissionAdmin(VersionAdmin, EmissionChildAdmin):
    base_model = EndOfLifeEmission
    list_display = EmissionAdmin.list_display + ("weight", "reference")
    list_filter = ("reference",)
    show_in_index = True

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