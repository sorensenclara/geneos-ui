from django.apps import AppConfig


class GeneosUiConfig(AppConfig):
    name = "geneos_ui"
    verbose_name = "GENEOS UI"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import checks  # noqa: F401  (registra los system checks)
