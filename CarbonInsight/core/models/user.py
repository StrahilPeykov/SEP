from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    This model can be used to add additional fields or methods
    specific to the application's user requirements.
    """
    # Add any additional fields or methods here if needed
    pass