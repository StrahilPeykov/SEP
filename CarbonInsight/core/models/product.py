from typing import Optional

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from core.models.lifecycle_stage import LifecycleStage


class Product(models.Model):
    name = models.CharField(max_length=255)
    supplier = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="products",
    )
    description = models.TextField(null=True, blank=True)
    manufacturer = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    emissions = GenericRelation("Emission")
    is_public = models.BooleanField(default=True)
    co_2_emissions_override = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
    )

    def calculate_emissions(self) -> Optional[dict[LifecycleStage, float]]:
        if self.co_2_emissions_override is not None:
            return {LifecycleStage.OTHER: self.co_2_emissions_override}
        return {}

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]

    def __str__(self):
        return self.name