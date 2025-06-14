from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q, CheckConstraint


if TYPE_CHECKING:
    from core.models.company import Company

class ProductSharingRequestStatus(models.TextChoices):
    """
    Enum for product sharing request status
    """

    PENDING = "Pending", "Pending"
    ACCEPTED = "Accepted", "Accepted"
    REJECTED = "Rejected", "Rejected"
    NOT_REQUESTED = "Not requested", "Not requested"

class ProductSharingRequest(models.Model):
    """
    Class representing a product sharing request.
    """

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="product_sharing_requests",
    )
    requester = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="requester"
    )
    status:ProductSharingRequestStatus = models.CharField(
        max_length=20,
        choices=[
            (choice.value, choice.label)
            for choice in ProductSharingRequestStatus
            if choice is not ProductSharingRequestStatus.NOT_REQUESTED
        ],
        default=ProductSharingRequestStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def supplier(self) -> "Company":
        """
        Returns the supplier of the product.

        Returns:
            Company object which supplies the child product
        """

        return self.product.supplier

    def clean(self):
        """
        Raises validation errors if the supplier and the requester are the same Company.

        Raises:
            ValidationError
        """

        if self.product.supplier == self.requester:
            raise ValidationError(
                {"requester": "Requester must be different from the supplier."}
            )

    def save(self, *args, **kwargs):
        """
        Forces a full clean on every save.
        """

        self.full_clean()
        super(ProductSharingRequest, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Product sharing request"
        verbose_name_plural = "Product sharing requests"
        ordering = ["-created_at"]
        unique_together = ("product", "requester")

    def __str__(self) -> str:
        """
        __str__ override that returns the Product, Requester and the ProductSharingRequestStatus as string.

        Returns:
            A str containing Product, Requester, ProductSharingRequestStatus
        """

        return f"{self.product} requested by {self.requester} is {self.status}"