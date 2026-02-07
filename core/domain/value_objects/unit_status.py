"""
Unit status enumeration for railway maintenance units.

Defines the operational states a maintenance unit can be in.
"""

from enum import Enum


class UnitStatus(Enum):
    """
    Operational status of a maintenance unit.

    Attributes:
        AVAILABLE: Unit is available for service (Disponible).
        DISABLED: Unit is temporarily out of service (Detenida).
        IN_MAINTENANCE: Unit undergoing scheduled/preventive maintenance
            (En mantenimiento preventivo/programado).
        UNDER_REPAIR: Unit undergoing corrective repairs
            (En reparación correctiva).
        RETIRED: Unit permanently out of service (Fuera de servicio).
    """

    AVAILABLE = "available"
    DISABLED = "disabled"
    IN_MAINTENANCE = "in_maintenance"
    UNDER_REPAIR = "under_repair"
    RETIRED = "retired"

    def __str__(self) -> str:
        """Return human-readable status name."""
        return self.value.replace("_", " ").title()

    @property
    def is_operational(self) -> bool:
        """Check if unit can potentially be in service."""
        return self in (UnitStatus.AVAILABLE, UnitStatus.DISABLED)

    @property
    def is_in_workshop(self) -> bool:
        """Check if unit is currently in workshop."""
        return self in (UnitStatus.IN_MAINTENANCE, UnitStatus.UNDER_REPAIR)
