from django.dispatch import receiver

from axes.signals import user_locked_out
from rest_framework.exceptions import PermissionDenied


@receiver(user_locked_out)
def on_user_locked_out(*args, **kwargs):
    raise PermissionDenied(
        "Too many failed login attempts, please try again later or contact support to unlock your account.")