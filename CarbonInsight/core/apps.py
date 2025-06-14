from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Application configuration for the core app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """
        Perform application initialization tasks.
        """
        import core.signals  # noqa