from django.core.validators import MinValueValidator
from django.db import models

from .emission import Emission
from .lifecycle_stage import LifecycleStage


class ProductionEnergyEmission(Emission):
    energy_consumption = models.FloatField(
        validators=[MinValueValidator(0.0)],
    )
    reference = models.ForeignKey(
        "ProductionEnergyEmissionReference",
        on_delete=models.CASCADE,
        related_name="production_emissions",
    )

    def calculate_emissions(self) -> dict[LifecycleStage, float]:
        return {LifecycleStage.OTHER: 0}
    calculate_emissions.short_description = "Emissions"

    class Meta:
        verbose_name = "Production energy emission"
        verbose_name_plural = "Production energy emissions"

    def __str__(self):
        return f"{self.energy_consumption}kWh (Production energy) for {self.content_object}"

class ProductionEnergyEmissionReference(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Production energy emission reference"
        verbose_name_plural = "Production energy emission references"

    def __str__(self):
        return self.name

class ProductionEnergyEmissionReferenceFactor(models.Model):
    emission_reference = models.ForeignKey(
        "ProductionEnergyEmissionReference",
        on_delete=models.CASCADE,
        related_name="reference_factors",
    )
    lifecycle_stage = models.CharField(
        max_length=255,
        choices=LifecycleStage.choices,
        default=LifecycleStage.OTHER,
    )
    co_2_emission_factor = models.FloatField(
        validators=[MinValueValidator(0.0)],
    )

    class Meta:
        verbose_name = "Production energy emission reference factor"
        verbose_name_plural = "Production energy emission reference factors"
        unique_together = ("emission_reference", "lifecycle_stage")