from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError as DjangoIntegrityError
from rest_framework.exceptions import ValidationError as DRFValidationError
from drf_standardized_errors.handler import ExceptionHandler

class DRFExceptionHandler(ExceptionHandler):
    def convert_known_exceptions(self, exc: Exception) -> Exception:
        """
        Converts known Django exceptions into DRF standardized errors.
        """
        if isinstance(exc, DjangoValidationError):
            # .message_dict is a {field: [errors]} mapping;
            # exc.messages is a flat list of strings
            detail = getattr(exc, "message_dict", None) or exc.messages
            return DRFValidationError(detail=detail)

        elif isinstance(exc, DjangoIntegrityError):
            # put the raw error message(s) under non_field_errors
            detail = {"non_field_errors": exc.args}
            return DRFValidationError(detail=detail)

        # Fall back to handling 404s, PermissionDenied, etc.
        return super().convert_known_exceptions(exc)