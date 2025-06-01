from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from .emission import Emission
from .emission_trace import EmissionTrace, EmissionTraceMentionClass, EmissionTraceMention, EmissionSplit
from .lifecycle_stage import LifecycleStage
from .reference_impact_unit import ReferenceImpactUnit


class UserEnergyEmission(Emission):
    energy_consumption = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Energy consumption in kWh",
    )
    reference = models.ForeignKey(
        "UserEnergyEmissionReference",
        on_delete=models.CASCADE,
        related_name="user_emissions",
        help_text="Reference values for the user energy emission",
        blank=True, null=True
    )

    def _get_emission_trace(self) -> EmissionTrace:
        if self.reference is None:
            reference_emission_trace = EmissionTrace(
                label="User energy consumption emission",
                reference_impact_unit=ReferenceImpactUnit.KILOWATT_HOUR,
                related_object=self,
            )
        else:
            reference_emission_trace = self.reference.get_emission_trace()

        # Multiply by the factor
        reference_multiplied_factor = reference_emission_trace * self.energy_consumption
        reference_multiplied_factor.label = f"User energy consumption emission"
        reference_multiplied_factor.methodology = f"{self.energy_consumption}kWh * {self.reference.name}"

        return reference_multiplied_factor

    class Meta:
        verbose_name = "User energy emission"
        verbose_name_plural = "User energy emissions"

    def __str__(self):
        return f"{self.energy_consumption}kWh (User energy) for {self.parent_product.name}"

class UserEnergyEmissionReference(models.Model):
    common_name  = models.CharField(max_length=255, null=True, blank=True)
    technical_name = models.CharField(max_length=255, null=True, blank=True)

    @property
    def name(self) -> str:
        if self.common_name is not None:
            return self.common_name
        if self.technical_name is not None:
            return self.technical_name
        return "MISSING BOTH COMMON AND TECHNICAL NAME"

    class Meta:
        verbose_name = "User energy emission reference"
        verbose_name_plural = "User energy emission references"
        constraints = [
            models.CheckConstraint(
                check=Q(common_name__isnull=False) | Q(technical_name__isnull=False),
                name='common_or_technical_name_not_null_user_energy_reference'
            ),
        ]

    def get_emission_trace(self) -> EmissionTrace:
        root = EmissionTrace(
            label=f"Reference values for {self.name}",
            methodology=f"Database lookup",
            reference_impact_unit=ReferenceImpactUnit.KILOWATT_HOUR,
            related_object=self
        )
        # Go through all factors and add them to the root
        for factor in self.reference_factors.all():
            root.emissions_subtotal[LifecycleStage(factor.lifecycle_stage)] = EmissionSplit(
                biogenic=factor.co_2_emission_factor_biogenic,
                non_biogenic=factor.co_2_emission_factor_non_biogenic
            )
        root.mentions.append(EmissionTraceMention(
            mention_class=EmissionTraceMentionClass.INFORMATION,
            message="Estimated values"
        ))
        return root
    get_emission_trace.short_description = "Emissions trace"

    def __str__(self):
        return self.name

class UserEnergyEmissionReferenceFactor(models.Model):
    emission_reference = models.ForeignKey(
        "UserEnergyEmissionReference",
        on_delete=models.CASCADE,
        related_name="reference_factors",
    )
    lifecycle_stage = models.CharField(
        max_length=255,
        choices=LifecycleStage.choices,
        default=LifecycleStage.OTHER,
    )
    co_2_emission_factor_biogenic = models.FloatField(default=0.0)
    co_2_emission_factor_non_biogenic = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "User energy emission reference factor"
        verbose_name_plural = "User energy emission reference factors"
        unique_together = ("emission_reference", "lifecycle_stage")