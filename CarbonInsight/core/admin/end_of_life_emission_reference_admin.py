from django.contrib import admin
from reversion.admin import VersionAdmin

from core.models import EndOfLifeEmissionReference, EndOfLifeEmissionReferenceFactor


class EndOfLifeEmissionReferenceFactorInline(admin.TabularInline):
    model = EndOfLifeEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor")
    extra = 0

@admin.register(EndOfLifeEmissionReference)
class EndOfLifeReferenceEmissionAdmin(VersionAdmin):
    list_display = ("name", "landfill_percentage", "incineration_percentage", "recycled_percentage", "reused_percentage")
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [EndOfLifeEmissionReferenceFactorInline]