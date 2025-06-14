import logging
from typing import Union, Literal, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from rest_framework.exceptions import ValidationError

from .emission_trace import EmissionTrace
from .product_sharing_request import ProductSharingRequestStatus, ProductSharingRequest
from .lifecycle_stage import LifecycleStage

logger = logging.getLogger(__name__)

class ProductBoMLineItem(models.Model):
    """
    Class modeling the link between product and the sub-product used in the parent product.
    """

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

    def clean(self):
        """
        Raises a validation error if the ProductBoMLineItem creates a cyclical dependency.

        Raises:
            ValidationError
        """

        super().clean()
        if self._creates_cycle():
            raise ValidationError("Cycle detected in BoM: this would create a loop")

    def _creates_cycle(self) -> bool:
        """
        Checks if the ProductBoMLineItem creates a cyclical dependency.

        Returns:
            True if the ProductBoMLineItem creates a cyclical dependency in the database.
        """

        start = self.parent_product
        target = self.line_item_product
        visited = set()

        def dfs(prod):
            if prod.id == start.id:
                return True
            for li in prod.line_items.all():
                child = li.line_item_product
                if child.id in visited:
                    continue
                visited.add(child.id)
                if dfs(child):
                    return True
            return False

        return dfs(target)

    def save(self, *args, **kwargs):
        # enforce clean() on save
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Product BoM line item"
        verbose_name_plural = "Product BoM line items"
        unique_together = ("parent_product", "line_item_product")
        constraints = [
            models.CheckConstraint(
                check=~Q(parent_product=F("line_item_product")),
                name="prevent_self_reference_bom_line_item"
            )
        ]

    def __str__(self) -> str:
        """
        __str__ override that returns the Product name, sub-product name and the quantity of the sub-product as string.

        Returns:
            Product name, sub-product name and the quantity of the sub-product.
        """

        return f"{self.parent_product.name}/{self.line_item_product.name} x{self.quantity}"

    @property
    def product_sharing_request(self) -> Optional[ProductSharingRequest]:
        """
        Returns the product sharing request for the sub-product.

        Returns:
            ProductSharingRequest object
        """

        return self.line_item_product.product_sharing_requests.filter(
            requester=self.parent_product.supplier
        ).first()

    @property
    def product_sharing_request_status(self) -> ProductSharingRequestStatus:
        """
        Returns the product sharing request status for the sub-product. Returns ProductSharingRequestStatus.ACCEPTED
         if the auto approve flag is set or if the parent product and child product are made by the same Company.

        Returns:
            ProductSharingRequestStatus
        """

        if self.line_item_product.supplier.auto_approve_product_sharing_requests:
            return ProductSharingRequestStatus.ACCEPTED
        if self.line_item_product.supplier == self.parent_product.supplier:
            return ProductSharingRequestStatus.ACCEPTED
        psr = self.product_sharing_request
        if psr is None:
            return ProductSharingRequestStatus.NOT_REQUESTED
        return psr.status