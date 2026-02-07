"""
Domain layer for the ARS_MP railway maintenance system.

Contains pure domain entities and value objects without framework dependencies.
"""

from core.domain.entities import (
    Coach,
    EMU,
    EmuConfiguration,
    Formation,
    MaintenanceUnit,
)
from core.domain.value_objects import CoachType, UnitStatus, UnitType

__all__ = [
    # Entities
    "MaintenanceUnit",
    "Coach",
    "EMU",
    "Formation",
    "EmuConfiguration",
    # Value Objects
    "UnitStatus",
    "UnitType",
    "CoachType",
]
