"""
Value objects for the ARS_MP railway maintenance system.

Immutable objects that describe characteristics of domain entities.
"""

from core.domain.value_objects.unit_type import UnitType
from core.domain.value_objects.coach_type import CoachType

__all__ = [
    "UnitType",
    "CoachType",
]
