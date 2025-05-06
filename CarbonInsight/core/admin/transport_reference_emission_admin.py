from django.contrib import admin
from reversion.admin import VersionAdmin

from core.models import TransportEmissionReference, TransportEmissionReferenceFactor


class TransportEmissionReferenceFactorInline(admin.TabularInline):
    model = TransportEmissionReferenceFactor
    fields = ("lifecycle_stage", "co_2_emission_factor")
    extra = 0

@admin.register(TransportEmissionReference)
class TransportReferenceEmissionAdmin(VersionAdmin):
    list_display = ("name", )
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [TransportEmissionReferenceFactorInline]