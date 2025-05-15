from django.core.exceptions import ValidationError
from django.db import models
class EmissionBoMLink(models.Model):
    emission = models.ForeignKey("Emission", on_delete=models.CASCADE)
    line_item = models.ForeignKey("ProductBoMLineItem", on_delete=models.CASCADE)

    def clean(self):
        if self.emission.parent_product_id != self.line_item.parent_product_id:
            raise ValidationError(
                "The emission and the BoM line item must belong to the same parent product."
            )

    class Meta:
        verbose_name = "Emission BoM link"
        verbose_name_plural = "Emission BoM links"
        unique_together = ("emission", "line_item")

    def __str__(self):
        return f"{self.emission} linked to {self.line_item}"