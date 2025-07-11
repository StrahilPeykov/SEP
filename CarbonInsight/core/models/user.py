from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    This model can be used to add additional fields or methods
    specific to the application's user requirements.
    """
    # Make email unique
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        __str__ override returning username, first name and last name of the user.

        Returns:
            A string containing username, first name and last name of the user
        """

        return f"{self.username} ({self.first_name} {self.last_name})"