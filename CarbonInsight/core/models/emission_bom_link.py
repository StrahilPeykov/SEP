from django.core.exceptions import ValidationError
from django.db import models
class EmissionBoMLink(models.Model):
    """
    Model that representing the relation between an emission and the BoM item they are linked to.
    """

    emission = models.ForeignKey("Emission", on_delete=models.CASCADE)
    line_item = models.ForeignKey("ProductBoMLineItem", on_delete=models.CASCADE)

    def clean(self):
        """
        The function that checks if both the emission and the product that the emission is tied to are linked under the
         same product.
        """

        if self.emission.parent_product_id != self.line_item.parent_product_id:
            raise ValidationError(
                "The emission and the BoM line item must belong to the same parent product."
            )

    def save(self, *args, **kwargs):
        """
        Forces a full clean on every save.
        """

        self.full_clean()
        super(EmissionBoMLink, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Emission BoM link"
        verbose_name_plural = "Emission BoM links"
        unique_together = ("emission", "line_item")

    def __str__(self) -> str:
        """
        __str__ override that returns the name of the emission and the name of the BoM item it is linked to.
        """

        return f"{self.emission} linked to {self.line_item}"