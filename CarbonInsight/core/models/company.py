from django.db import models
from .user import User

class Company(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(
        User,
        through='CompanyMembership',
        related_name='companies'
    )

    def __str__(self):
        return self.name