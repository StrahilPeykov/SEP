import logging
from typing import Optional

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from .emission_trace import EmissionTrace, EmissionTraceMentionClass, EmissionTraceMention, EmissionTraceChild
from .lifecycle_stage import LifecycleStage
from .product_sharing_request import ProductSharingRequest, ProductSharingRequestStatus

logger = logging.getLogger(__name__)

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
    # is_public describes whether the product is listed on the public catalogue
    is_public = models.BooleanField(default=True)

    def request(self, requester: "Company", user: "User") -> "ProductSharingRequest":
        # Block requests to your own company
        if requester == self.supplier:
            raise ValueError("You cannot request access to your own product.")
        # Block requests to private products
        if not self.is_public:
            raise ValueError("You cannot request access to a private product.")
        return ProductSharingRequest.objects.get_or_create(
            product=self,
            requester=requester,
        )

    def get_emission_trace(self) -> EmissionTrace:
        root = EmissionTrace(
            label=f"Product: {self.name}",
            methodology=f"Sum up all the product-level emissions and its line items' emissions."
        )
        # Add own emissions
        for emission_obj in self.emissions.all():
            emission_obj_real: "Emission" = emission_obj.get_real_instance()
            if emission_obj_real is None:
                logger.warning(f"Emission {emission_obj} has no content object.")
                continue
            emission_trace = emission_obj_real.get_emission_trace()
            root.children.add(EmissionTraceChild(
                emission_trace=emission_trace,
                quantity=emission_obj_real.quantity
            ))

        # Add emissions from line items
        for line_item in self.line_items.all():
            # Check if the line item is shared and if the request is accepted
            if line_item.product_sharing_request is None:
                emission_trace = EmissionTrace(label=f"Product: {self.name}")
                emission_trace.mentions.append(EmissionTraceMention(
                    mention_class=EmissionTraceMentionClass.ERROR,
                    message="You have not requested access to this product's PCF data yet."
                ))
                continue

            if line_item.product_sharing_request.status == ProductSharingRequestStatus.PENDING:
                emission_trace = EmissionTrace(label=f"Product: {self.name}")
                emission_trace.mentions.append(EmissionTraceMention(
                    mention_class=EmissionTraceMentionClass.ERROR,
                    message=f"{line_item.product_sharing_request.supplier.name} "
                            f"has not accepted your PCF data sharing request yet."
                ))
                continue

            if line_item.product_sharing_request.status == ProductSharingRequestStatus.REJECTED:
                emission_trace = EmissionTrace(label=f"Product: {self.name}")
                emission_trace.mentions.append(EmissionTraceMention(
                    mention_class=EmissionTraceMentionClass.ERROR,
                    message=f"{line_item.product_sharing_request.supplier.name} "
                            f"has rejected your PCF data sharing request."
                ))
                continue

            # Get the line item's emissions
            emission_trace = line_item.line_item_product.get_emission_trace()
            # Add the line item to the root
            root.children.add(EmissionTraceChild(
                emission_trace=emission_trace,
                quantity=line_item.quantity
            ))

        root.sum_up()

        # Check if there are any EmissionOverrideFactors
        # If so, replace the emission trace with the overridden values
        if self.override_factors.exists():
            root.emissions_subtotal.clear()
            root.methodology = "User-provided values"
            root.mentions.append(EmissionTraceMention(
                mention_class=EmissionTraceMentionClass.WARNING,
                message="Emission factors are overridden by user-provided values"
            ))
            for factor in self.override_factors.all():
                root.emissions_subtotal[factor.lifecycle_stage] = factor.co_2_emission_factor

        return root
    get_emission_trace.short_description = "Emissions trace"


    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]

    def __str__(self):
        return self.name

class ProductEmissionOverrideFactor(models.Model):
    emission = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="override_factors",
    )
    lifecycle_stage = models.CharField(
        max_length=255,
        choices=LifecycleStage.choices,
        default=LifecycleStage.OTHER,
    )
    co_2_emission_factor = models.FloatField()