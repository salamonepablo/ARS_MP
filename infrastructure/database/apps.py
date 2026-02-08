"""
Django app configuration for infrastructure.database.

This app contains Django models that persist domain entities.
"""

from django.apps import AppConfig


class DatabaseConfig(AppConfig):
    """Configuration for the database app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "infrastructure.database"
    verbose_name = "Base de Datos de Flota"
