from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from polymorphic.models import PolymorphicModel

from .lifecycle_stage import LifecycleStage
from .product import Product
from .product_bom_line_item import  ProductBoMLineItem

class Emission(PolymorphicModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    content_object.short_description = "Linked product/line item"

    class Meta:
        verbose_name = "Emission"
        verbose_name_plural = "Emissions"

    def clean(self):
        allowed_types = (Product, ProductBoMLineItem)
        if self.content_object and not isinstance(self.content_object, allowed_types):
            raise ValidationError("Emission can only be attached to Product or ProductBoMLineItem.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def calculate_emissions(self) -> dict[LifecycleStage, float]:
        if False:  # TODO: Replace with lookup on EmissionOverrideFactor. If any factors exist, return them instead.
            return {LifecycleStage.OTHER: 0}
        return self.get_real_instance().calculate_emissions()
    calculate_emissions.short_description = "Emissions"

    def __str__(self):
        return f"{self.content_object} has {self.calculate_emissions()} gCO2e"
    
class EmissionOverrideFactor(models.Model):
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
    co_2_emission_factor = models.FloatField()