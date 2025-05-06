from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    vat_number = models.CharField(max_length=255, unique=True)
    business_registration_number = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(
        "User", through="CompanyMembership", related_name="companies"
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def user_has_permission(self, user) -> bool:
        return self.users.filter(id=user.id).exists()

    def __str__(self):
        return self.name
