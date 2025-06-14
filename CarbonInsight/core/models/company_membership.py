from django.db import models


class CompanyMembership(models.Model):
    """
    Model to represent a company membership
    """

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Company membership"
        verbose_name_plural = "Company memberships"
        unique_together = ("user", "company")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        """
        __str__ override that returns the user and the user is part of as str

        Returns:
            str containing the user and the company
        """
        return f"{self.user} is a member of {self.company}"