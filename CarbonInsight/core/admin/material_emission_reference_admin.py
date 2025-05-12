from django.contrib import admin
from reversion.admin import VersionAdmin

from core.models import MaterialEmissionReference, MaterialEmissionReferenceFactor


class MaterialEmissionReferenceFactorInline(admin.TabularInline):
    model = MaterialEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor")
    extra = 0

@admin.register(MaterialEmissionReference)
class MaterialReferenceEmissionAdmin(VersionAdmin):
    list_display = ("name", )
    search_fields = ("name",)
    inlines = [MaterialEmissionReferenceFactorInline]