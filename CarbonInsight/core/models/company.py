from django.db import models
from django.db.models import Q


class Company(models.Model):
    name = models.CharField(max_length=255)
    vat_number = models.CharField(max_length=255, unique=True)
    business_registration_number = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(
        "User", through="CompanyMembership", related_name="companies"
    )
    is_reference = models.BooleanField(default=False)
    auto_approve_product_sharing_requests = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_reference"],
                condition=Q(is_reference=True),
                name="unique_reference_company"
            )
        ]

    def user_is_member(self, user) -> bool:
        return self.users.filter(id=user.id).exists()

    def __str__(self):
        return self.name
