"""
EMU (Electric Multiple Unit) entity.

An EMU is a self-propelled electric train composed of multiple coaches.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from core.domain.entities.maintenance_unit import MaintenanceUnit
from core.domain.value_objects.unit_type import UnitType

if TYPE_CHECKING:
    from core.domain.entities.coach import Coach
    from core.domain.entities.emu_configuration import EmuConfiguration


@dataclass(kw_only=True)
class EMU(MaintenanceUnit):
    """
    Electric Multiple Unit: composed of N coaches.

    Represents a complete trainset that operates as a single unit.
    Composed of individual coaches (motor and trailer).

    CSR EMUs typically have 3-4 coaches: [MC1, R1, R2, MC2] or [MC1, R1, MC2]
    Toshiba EMUs typically have 3-4 coaches: [M, R, RP, M] or [M, R, M]

    Attributes:
        voltage: Operating voltage in volts (25000 for AC 25kV).
        max_speed: Maximum speed in km/h.
        total_passenger_capacity: Total passenger capacity across all coaches.
        coaches: List of Coach entities composing this EMU.
        formation_id: UUID of the Formation this EMU belongs to (optional).
        configuration_id: UUID of EmuConfiguration defining valid composition.

    Raises:
        ValueError: If EMU has less than 2 coaches, or coaches are from
            different manufacturers.
    """

    voltage: int
    max_speed: int
    total_passenger_capacity: int
    coaches: list["Coach"] = field(default_factory=list)
    formation_id: UUID | None = None
    configuration_id: UUID | None = None

    def get_unit_type(self) -> UnitType:
        """Return EMU as the unit type."""
        return UnitType.EMU

    def __post_init__(self) -> None:
        """Validate EMU data after initialization."""
        super().__post_init__()
        self._validate_composition()

    def _validate_composition(self) -> None:
        """
        Validate that EMU has valid coach composition.

        Raises:
            ValueError: If composition is invalid.
        """
        if len(self.coaches) < 2:
            raise ValueError("EMU must have at least 2 coaches")

        # Verify all coaches are from the same manufacturer
        if self.coaches:
            manufacturers = {coach.manufacturer for coach in self.coaches}
            if len(manufacturers) > 1:
                raise ValueError("All coaches must be from same manufacturer")

    def get_motor_coaches(self) -> list["Coach"]:
        """
        Return all coaches with traction.

        Returns:
            List of motor coaches (MC1, MC2 for CSR; M for Toshiba).
        """
        return [c for c in self.coaches if c.is_motor_coach()]

    def get_trailer_coaches(self) -> list["Coach"]:
        """
        Return all non-motor coaches.

        Returns:
            List of trailer coaches (R1, R2 for CSR; R, RP for Toshiba).
        """
        return [c for c in self.coaches if c.is_trailer_coach()]

    def get_coach_count(self) -> int:
        """Return the number of coaches in this EMU."""
        return len(self.coaches)

    def validate_configuration(self, config: "EmuConfiguration") -> None:
        """
        Validate this EMU against a configuration.

        Args:
            config: EmuConfiguration to validate against.

        Raises:
            ValueError: If EMU doesn't match configuration.
        """
        config.validate(self.coaches)
