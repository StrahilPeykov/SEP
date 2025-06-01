from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from .emission import Emission
from .emission_trace import EmissionTrace, EmissionTraceMentionClass, EmissionTraceMention, EmissionSplit
from .lifecycle_stage import LifecycleStage
from .reference_impact_unit import ReferenceImpactUnit


class TransportEmission(Emission):
    distance = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Distance of the transport in km",
    )
    weight = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Weight of the transported product in kg",
    )
    reference = models.ForeignKey(
        "TransportEmissionReference",
        on_delete=models.CASCADE,
        related_name="transport_emissions",
        help_text="Reference values for the transport emission",
        blank=True, null=True
    )

    @property
    def tkm(self):
        return self.weight * self.distance

    def _get_emission_trace(self) -> EmissionTrace:
        if self.reference is None:
            reference_multiplied_factor = EmissionTrace(
                label="Transport emission",
                reference_impact_unit=ReferenceImpactUnit.KILOWATT_HOUR,
                related_object=self,
            )
        else:
            # Multiply by the factor
            reference_multiplied_factor = self.reference.get_emission_trace() * self.tkm
            reference_multiplied_factor.label = f"Transport emission"
            reference_multiplied_factor.methodology = f"{self.weight}kg * {self.distance}km * {self.reference.name}"

        return reference_multiplied_factor

    class Meta:
        verbose_name = "Transport emission"
        verbose_name_plural = "Transport emissions"

    def __str__(self):
        out = f"{self.tkm}tkm (Transport) for {self.parent_product.name}/"
        if self.line_items.exists():
            for line_item in self.line_items.all():
                 out += f"{line_item.line_item_product.name}, "
        return out.strip("/").strip(", ")

class TransportEmissionReference(models.Model):
    common_name = models.CharField(max_length=255, null=True, blank=True)
    technical_name = models.CharField(max_length=255, null=True, blank=True)

    @property
    def name(self) -> str:
        if self.common_name is not None:
            return self.common_name
        if self.technical_name is not None:
            return self.technical_name
        # This return exists to prevent Django from crashing
        # when the changes exist solely in memory.
        return "MISSING BOTH COMMON AND TECHNICAL NAME"

    class Meta:
        verbose_name = "Transport emission reference"
        verbose_name_plural = "Transport emission references"
        constraints = [
            models.CheckConstraint(
                check=Q(common_name__isnull=False) | Q(technical_name__isnull=False),
                name='common_or_technical_name_not_null_transport_emission_reference'
            ),
        ]

    def get_emission_trace(self) -> EmissionTrace:
        root = EmissionTrace(
            label=f"Reference values for {self.name}",
            methodology=f"Database lookup",
            reference_impact_unit=ReferenceImpactUnit.KILOGRAM,
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

class TransportEmissionReferenceFactor(models.Model):
    emission_reference = models.ForeignKey(
        "TransportEmissionReference",
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
        verbose_name = "Transport emission reference factor"
        verbose_name_plural = "Transport emission reference factors"
        unique_together = ("emission_reference", "lifecycle_stage")