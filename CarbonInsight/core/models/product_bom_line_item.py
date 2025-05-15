import logging
from typing import Union, Literal, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models

from .emission_trace import EmissionTrace
from .product_sharing_request import ProductSharingRequestStatus, ProductSharingRequest
from .lifecycle_stage import LifecycleStage

logger = logging.getLogger(__name__)

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

    class Meta:
        verbose_name = "Product BoM line item"
        verbose_name_plural = "Product BoM line items"
        unique_together = ("parent_product", "line_item_product")

    def __str__(self):
        return f"{self.parent_product.name}/{self.line_item_product.name} x{self.quantity}"

    @property
    def product_sharing_request(self) -> Optional[ProductSharingRequest]:
        return self.line_item_product.product_sharing_requests.filter(
            requester=self.parent_product.supplier
        ).first()