"""
Unit type enumeration for railway maintenance units.

Defines the hierarchical types of maintenance units.
"""

from enum import Enum


class UnitType(Enum):
    """
    Type of maintenance unit in the railway hierarchy.

    Attributes:
        FORMATION: Complete train formation (1+ EMUs operating together).
        EMU: Electric Multiple Unit (composed of N coaches).
        COACH: Individual coach within an EMU.
    """

    FORMATION = "formation"
    EMU = "emu"
    COACH = "coach"

    def __str__(self) -> str:
        """Return human-readable type name."""
        return self.value.upper()
