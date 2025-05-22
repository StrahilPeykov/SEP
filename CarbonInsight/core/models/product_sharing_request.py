from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q, CheckConstraint


class ProductSharingRequestStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    ACCEPTED = "Accepted", "Accepted"
    REJECTED = "Rejected", "Rejected"
    NOT_REQUESTED = "Not requested", "Not requested"

class ProductSharingRequest(models.Model):
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
    def supplier(self):
        return self.product.supplier

    def clean(self):
        if self.product.supplier == self.requester:
            raise ValidationError(
                {"requester": "Requester must be different from the supplier."}
            )

    class Meta:
        verbose_name = "Product sharing request"
        verbose_name_plural = "Product sharing requests"
        ordering = ["-created_at"]
        unique_together = ("product", "requester")

    def __str__(self):
        return f"{self.product} requested by {self.requester} is {self.status}"