from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models

class ProductBoMLineItem(models.Model):
    parent_product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    line_item_product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="used_in_line_items",
    )
    quantity = models.FloatField(
        validators=[MinValueValidator(0.0)],
    )
    emissions = GenericRelation("Emission")

    class Meta:
        verbose_name = "Product BoM line item"
        verbose_name_plural = "Product BoM line items"

    def __str__(self):
        return f"{self.parent_product.name}/{self.line_item_product.name} x{self.quantity}"