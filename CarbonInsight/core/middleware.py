from auditlog.context import set_actor
from auditlog.middleware import AuditlogMiddleware as _AuditlogMiddleware
from django.utils.functional import SimpleLazyObject


class AuditlogMiddleware(_AuditlogMiddleware):
    """
    Custom auditlog middleware that sets the actor context because DRF
    sets the user on the VIEW level not on MIDDLEWARE level.
    See https://github.com/jazzband/django-auditlog/issues/115
    """
    def __call__(self, request):
        remote_addr = self._get_remote_addr(request)

        user = SimpleLazyObject(lambda: getattr(request, "user", None))

        context = set_actor(actor=user, remote_addr=remote_addr)

        with context:
            return self.get_response(request)