"""Fleet app configuration."""

from django.apps import AppConfig


class FleetConfig(AppConfig):
    """Configuration for the Fleet management app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "web.fleet"
    verbose_name = "Gestión de Flota"
