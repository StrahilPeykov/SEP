from django.core.validators import MinValueValidator
from django.db import models

from .emission import Emission
from .lifecycle_stage import LifecycleStage


class MaterialEmission(Emission):
    weight = models.FloatField(
        validators=[MinValueValidator(0.0)],
    )
    reference = models.ForeignKey(
        "MaterialEmissionReference",
        on_delete=models.CASCADE,
        related_name="material_emissions",
    )

    def calculate_emissions(self) -> dict[LifecycleStage, float]:
        return {LifecycleStage.OTHER: 0}
    calculate_emissions.short_description = "Emissions"

    class Meta:
        verbose_name = "Material emission"
        verbose_name_plural = "Material emissions"

    def __str__(self):
        return f"{self.weight}kg (Material) for {self.content_object}"

class MaterialEmissionReference(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Material emission reference"
        verbose_name_plural = "Material emission references"

    def __str__(self):
        return self.name

class MaterialEmissionReferenceFactor(models.Model):
    emission_reference = models.ForeignKey(
        "MaterialEmissionReference",
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
        verbose_name = "Material emission reference factor"
        verbose_name_plural = "Material emission reference factors"
        unique_together = ("emission_reference", "lifecycle_stage")