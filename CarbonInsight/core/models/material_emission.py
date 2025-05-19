from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from .emission import Emission
from .emission_trace import EmissionTrace, EmissionTraceMentionClass, EmissionTraceMention, EmissionTraceSource
from .lifecycle_stage import LifecycleStage
from .reference_impact_unit import ReferenceImpactUnit


class MaterialEmission(Emission):
    weight = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Weight of the material in kg",
    )
    reference = models.ForeignKey(
        "MaterialEmissionReference",
        on_delete=models.CASCADE,
        related_name="material_emissions",
        help_text="Reference values for the material emission",
    )

    def _get_emission_trace(self) -> EmissionTrace:
        reference_emission_trace = self.reference.get_emission_trace()

        # Multiply by the factor
        reference_multiplied_factor = reference_emission_trace * self.weight
        reference_multiplied_factor.label = f"Material emission"
        reference_multiplied_factor.methodology = f"{self.weight}kg * {self.reference.name}"

        return reference_multiplied_factor

    class Meta:
        verbose_name = "Material emission"
        verbose_name_plural = "Material emissions"

    def __str__(self):
        return f"{self.weight}kg (Material) for {self.parent_product.name}"

class MaterialEmissionReference(models.Model):
    common_name = models.CharField(max_length=255, null=True, blank=True)
    technical_name = models.CharField(max_length=255, null=True, blank=True)

    @property
    def name(self) -> str:
        if self.common_name is not None:
            return self.common_name
        if self.technical_name is not None:
            return self.technical_name
        return "MISSING BOTH COMMON AND TECHNICAL NAME"

    class Meta:
        verbose_name = "Material emission reference"
        verbose_name_plural = "Material emission references"
        constraints = [
            models.CheckConstraint(
                check=Q(common_name__isnull=False) | Q(technical_name__isnull=False),
                name='common_or_technical_name_not_null_material_emission_reference'
            ),
        ]

    def get_emission_trace(self) -> EmissionTrace:
        root = EmissionTrace(
            label=f"Reference values for {self.name}",
            methodology=f"Database lookup",
            reference_impact_unit=ReferenceImpactUnit.KILOGRAM,
            source=EmissionTraceSource.MATERIAL,
        )
        # Go through all factors and add them to the root
        for factor in self.reference_factors.all():
            root.emissions_subtotal[LifecycleStage(factor.lifecycle_stage)] = factor.co_2_emission_factor
        root.mentions.append(EmissionTraceMention(
            mention_class = EmissionTraceMentionClass.INFORMATION,
            message = "Estimated values"
        ))
        return root
    get_emission_trace.short_description = "Emissions trace"

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
    co_2_emission_factor = models.FloatField()

    class Meta:
        verbose_name = "Material emission reference factor"
        verbose_name_plural = "Material emission reference factors"
        unique_together = ("emission_reference", "lifecycle_stage")