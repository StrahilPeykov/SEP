from django.db import models
from polymorphic.models import PolymorphicModel

from .emission_trace import EmissionTrace, EmissionTraceMentionClass, EmissionTraceMention, EmissionSplit
from .lifecycle_stage import LifecycleStage
from .pcf_calculation_method import PcfCalculationMethod
from .reference_impact_unit import ReferenceImpactUnit


class Emission(PolymorphicModel):
    """
    Abstract model that represents an emission.
    """

    parent_product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="emissions")
    quantity = models.FloatField(default=1)
    line_items = models.ManyToManyField(
        "ProductBoMLineItem",
        through="EmissionBoMLink",
        related_name="emissions",
    )
    pcf_calculation_method = models.CharField(
        max_length=255,
        choices=PcfCalculationMethod.choices,
        default=PcfCalculationMethod.ISO_14040_ISO_14044,
    )

    class Meta:
        verbose_name = "Emission"
        verbose_name_plural = "Emissions"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_emission_trace(self) -> EmissionTrace:
        """
        Calculates the PCF and returns a tree structured trace for emission that is to be used in DPP

        Returns:
            emission_trace: object of type EmissionTrace
        """

        real_instance = self.get_real_instance()
        emission_trace = real_instance._get_emission_trace()
        emission_trace.related_object = real_instance
        emission_trace.pcf_calculation_method = PcfCalculationMethod(self.pcf_calculation_method)

        # Check if there are any EmissionOverrideFactors
        # If so, replace the emission trace with the overridden values
        if self.override_factors.exists():
            emission_trace.emissions_subtotal.clear()
            emission_trace.methodology = "User-provided values"
            emission_trace.mentions.append(EmissionTraceMention(
                mention_class = EmissionTraceMentionClass.WARNING,
                message = "Emission factors are overridden by user-provided values"
            ))
            for factor in self.override_factors.all():
                emission_trace.emissions_subtotal[LifecycleStage(factor.lifecycle_stage)] = EmissionSplit(
                    biogenic=factor.co_2_emission_factor_biogenic,
                    non_biogenic=factor.co_2_emission_factor_non_biogenic
                )

        for line_item in self.line_items.all():
            emission_trace.mentions.append(EmissionTraceMention(
                mention_class = EmissionTraceMentionClass.INFORMATION,
                message = f"Used by {line_item.line_item_product.name}"
            ))
        return emission_trace
    get_emission_trace.short_description = "Emissions trace"

    def _get_emission_trace(self) -> EmissionTrace:
        """
        Abstract function that gets override by the children that inherits the class Emission.
        """

        # This is a placeholder for the actual implementation
        raise NotImplementedError("Subclasses must implement this method")

    def __str__(self) -> str:
        """
        __str__ override that returns the name of the product that this Class attached to and the total emission.

        Returns:
            name of the parent product of the emission and the total emission
        """

        return f"{self.parent_product.name} has {self.get_emission_trace()} gCO2e"
    
class EmissionOverrideFactor(models.Model):
    """
    Model representing the override that the emission can have which changes the total emission returned.
    """

    emission = models.ForeignKey(
        "Emission",
        on_delete=models.CASCADE,
        related_name="override_factors",
    )
    lifecycle_stage = models.CharField(
        max_length=255,
        choices=LifecycleStage.choices,
        default=LifecycleStage.OTHER,
    )
    co_2_emission_factor_biogenic = models.FloatField(default=0.0)
    co_2_emission_factor_non_biogenic = models.FloatField(default=0.0)