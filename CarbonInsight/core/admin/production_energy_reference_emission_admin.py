from django.contrib import admin
from reversion.admin import VersionAdmin

from core.models import ProductionEnergyEmissionReference, ProductionEnergyEmissionReferenceFactor


class ProductionEnergyEmissionReferenceFactorInline(admin.TabularInline):
    model = ProductionEnergyEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor")
    extra = 0

@admin.register(ProductionEnergyEmissionReference)
class ProductionEnergyReferenceEmissionAdmin(VersionAdmin):
    list_display = ("name", )
    search_fields = ("name",)
    inlines = [ProductionEnergyEmissionReferenceFactorInline]