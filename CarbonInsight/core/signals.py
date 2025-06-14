from django.dispatch import receiver

from axes.signals import user_locked_out
from rest_framework.exceptions import PermissionDenied


@receiver(user_locked_out)
def on_user_locked_out(*args, **kwargs):
    """
    Handler for the user_locked_out signal from django-axes.
    This function maps the alert to a PermissionDenied exception which is then handled by DRF.
    """
    raise PermissionDenied(
        "Too many failed login attempts, please try again later or contact support to unlock your account.")