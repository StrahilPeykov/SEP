from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q

from .emission import Emission
from .lifecycle_stage import LifecycleStage


class EndOfLifeEmission(Emission):
    weight = models.FloatField(
        validators=[MinValueValidator(0.0)],
    )
    reference = models.ForeignKey(
        "EndOfLifeEmissionReference",
        on_delete=models.CASCADE,
        related_name="transport_emissions",
    )

    def calculate_emissions(self) -> dict[LifecycleStage, float]:
        return {LifecycleStage.OTHER: 0}
    calculate_emissions.short_description = "Emissions"

    class Meta:
        verbose_name = "End of life emission"
        verbose_name_plural = "End of life emissions"

    def __str__(self):
        return f"{self.weight}kg (End of life) for {self.content_object}"

class EndOfLifeEmissionReference(models.Model):
    common_name = models.CharField(max_length=255, null=True, blank=True)
    technical_name = models.CharField(max_length=255, null=True, blank=True)

    landfill_percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    incineration_percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    recycled_percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    reused_percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )

    @property
    def name(self) -> str:
        if self.common_name is not None:
            return self.common_name
        if self.technical_name is not None:
            return self.technical_name
        return "MISSING BOTH COMMON AND TECHNICAL NAME"

    class Meta:
        verbose_name = "End of life emission reference"
        verbose_name_plural = "End of life emission references"
        constraints = [
            models.CheckConstraint(
                check=Q(common_name__isnull=False) | Q(technical_name__isnull=False),
                name='common_or_technical_name_not_null_end_of_life_emission_reference'
            ),
        ]

    def __str__(self):
        return self.name

class EndOfLifeEmissionReferenceFactor(models.Model):
    emission_reference = models.ForeignKey(
        "EndOfLifeEmissionReference",
        on_delete=models.CASCADE,
        related_name="reference_factors",
    )
    lifecycle_stage = models.CharField(
        max_length=255,
        choices=LifecycleStage.choices,
        default=LifecycleStage.OTHER,
    )
    co_2_emission_factor = models.FloatField()

    class Meta:
        verbose_name = "End of life emission reference factor"
        verbose_name_plural = "End of life emission reference factors"
        unique_together = ("emission_reference", "lifecycle_stage")