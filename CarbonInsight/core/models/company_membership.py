from django.db import models
from .user import User
from .company import Company

class CompanyMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)