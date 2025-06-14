from django.contrib import admin

from core.models import ProductionEnergyEmissionReference, ProductionEnergyEmissionReferenceFactor


class ProductionEnergyEmissionReferenceFactorInline(admin.TabularInline):
    """
    Defines the ProductionEnergyEmissionReferenceFactor fields to be presented inline when editing a
     ProductionEnergyEmissionReference.
    """

    model = ProductionEnergyEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")
    extra = 0

@admin.register(ProductionEnergyEmissionReference)
class ProductionEnergyReferenceEmissionAdmin(admin.ModelAdmin):
    """
    Defines the fields to be presented and how they are shown in the admin panel for ProductionEnergyEmissionReference.
    """

    list_display = ("name", "get_emission_total", "get_emission_trace",
                    "get_emission_total_non_biogenic", "get_emission_total_biogenic")
    search_fields = ("name",)
    inlines = [ProductionEnergyEmissionReferenceFactorInline]

    def get_emission_total(self, reference:ProductionEnergyEmissionReference) -> float:
        """
        Returns the emission total for provided ProductionEnergyEmissionReference object.

        Args:
            reference: ProductionEnergyEmissionReference object.
        Returns:
            total emission of the ProductionEnergyEmissionReference object
        """

        return reference.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"

    def get_emission_total_non_biogenic(self, emission: ProductionEnergyEmissionReference) -> float:
        """
        Returns the total non-biogenic emission for provided ProductionEnergyEmissionReference object.

        Args:
            reference: ProductionEnergyEmissionReference object.
        Returns:
            total non-biogenic emission of the ProductionEnergyEmissionReference object
        """

        return emission.get_emission_trace().total_non_biogenic

    get_emission_total_non_biogenic.short_description = "Total non-biogenic emissions"

    def get_emission_total_biogenic(self, emission: ProductionEnergyEmissionReference) -> float:
        """
        Returns the total biogenic emission for provided ProductionEnergyEmissionReference object.

        Args:
            reference: ProductionEnergyEmissionReference object.
        Returns:
            total biogenic emission of the ProductionEnergyEmissionReference object
        """

        return emission.get_emission_trace().total_biogenic

    get_emission_total_biogenic.short_description = "Total biogenic emissions"