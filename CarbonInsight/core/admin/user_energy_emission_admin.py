from django.contrib import admin

from core.models import UserEnergyEmissionReference, UserEnergyEmissionReferenceFactor


class UserEnergyEmissionReferenceFactorInline(admin.TabularInline):
    """
    Defines the UserEnergyEmissionReferenceFactor fields to be presented inline when editing a
     UserEnergyEmissionReference.
    """

    model = UserEnergyEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor_biogenic", "co_2_emission_factor_non_biogenic")
    extra = 0

@admin.register(UserEnergyEmissionReference)
class UserEnergyReferenceEmissionAdmin(admin.ModelAdmin):
    """
    Defines the fields to be presented and how they are shown in the admin panel for UserEnergyEmissionReference.
    """

    list_display = ("name", "get_emission_total", "get_emission_trace",
                    "get_emission_total_non_biogenic", "get_emission_total_biogenic")
    search_fields = ("name",)
    inlines = [UserEnergyEmissionReferenceFactorInline]

    def get_emission_total(self, reference:UserEnergyEmissionReference) -> float:
        """
        Returns the emission total for provided UserEnergyEmissionReference object.

        Args:
            reference: UserEnergyEmissionReference object.
        Returns:
            total emission of the UserEnergyEmissionReference object
        """

        return reference.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"

    def get_emission_total_non_biogenic(self, emission: UserEnergyEmissionReference) -> float:
        """
        Returns the total non-biogenic emission for provided UserEnergyEmissionReference object.

        Args:
            reference: UserEnergyEmissionReference object.
        Returns:
            total non-biogenic emission of the UserEnergyEmissionReference object
        """

        return emission.get_emission_trace().total_non_biogenic

    get_emission_total_non_biogenic.short_description = "Total non-biogenic emissions"

    def get_emission_total_biogenic(self, emission: UserEnergyEmissionReference) -> float:
        """
        Returns the total biogenic emission for provided UserEnergyEmissionReference object.

        Args:
            reference: UserEnergyEmissionReference object.
        Returns:
            total biogenic emission of the UserEnergyEmissionReference object
        """

        return emission.get_emission_trace().total_biogenic

    get_emission_total_biogenic.short_description = "Total biogenic emissions"