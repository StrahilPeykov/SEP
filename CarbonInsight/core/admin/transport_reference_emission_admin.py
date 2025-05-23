from django.contrib import admin
from reversion.admin import VersionAdmin

from core.models import TransportEmissionReference, TransportEmissionReferenceFactor


class TransportEmissionReferenceFactorInline(admin.TabularInline):
    model = TransportEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor")
    extra = 0

@admin.register(TransportEmissionReference)
class TransportReferenceEmissionAdmin(VersionAdmin):
    list_display = ("name", "get_emission_total", "get_emission_trace")
    search_fields = ("name",)
    inlines = [TransportEmissionReferenceFactorInline]

    def get_emission_total(self, reference:TransportEmissionReference) -> float:
        return reference.get_emission_trace().total
    get_emission_total.short_description = "Total emissions"