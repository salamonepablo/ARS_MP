"""
Domain entities for the ARS_MP railway maintenance system.

This module contains pure domain entities without any framework dependencies.
"""

from core.domain.entities.maintenance_unit import MaintenanceUnit
from core.domain.entities.coach import Coach
from core.domain.entities.emu import EMU
from core.domain.entities.formation import Formation
from core.domain.entities.emu_configuration import EmuConfiguration

__all__ = [
    "MaintenanceUnit",
    "Coach",
    "EMU",
    "Formation",
    "EmuConfiguration",
]
