from django.db import models

class ProductSharingRequestStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    ACCEPTED = "Accepted", "Accepted"
    REJECTED = "Rejected", "Rejected"

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
        choices=ProductSharingRequestStatus.choices,
        default=ProductSharingRequestStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_approved(self):
        return self.status == ProductSharingRequestStatus.ACCEPTED

    @property
    def supplier(self):
        return self.product.supplier

    class Meta:
        verbose_name = "Product sharing request"
        verbose_name_plural = "Product sharing requests"
        ordering = ["-created_at"]
        unique_together = ("product", "requester")

    def __str__(self):
        return f"{self.product} requested by {self.requester} is {self.status}"