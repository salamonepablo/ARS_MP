"""
Coach entity representing an individual railway coach.

A coach is a single car within an EMU (Electric Multiple Unit).
"""

from dataclasses import dataclass
from uuid import UUID

from core.domain.entities.maintenance_unit import MaintenanceUnit
from core.domain.value_objects.coach_type import CoachType
from core.domain.value_objects.unit_type import UnitType


@dataclass(kw_only=True)
class Coach(MaintenanceUnit):
    """
    Individual coach within an EMU formation.

    A coach can be a motor coach (with traction) or trailer coach (without).
    Motor coaches typically have driver cabins, while trailer coaches
    may have pantographs for power collection.

    Attributes:
        coach_type: Type of coach (MC1, MC2, R1, R2, M, R, RP).
        voltage: Operating voltage in volts (required for motor coaches, 25000V AC).
        has_pantograph: Whether this coach has a pantograph.
        has_cabin: Whether this coach has a driver cabin.
        place: Position within the EMU (1..N).
        seating_capacity: Number of passenger seats.
        emu_id: UUID of the EMU this coach belongs to (optional).

    Raises:
        ValueError: If seating_capacity is not positive,
            or motor coach lacks voltage specification.
    """

    coach_type: CoachType
    voltage: int | None
    has_pantograph: bool
    has_cabin: bool
    place: int | None
    seating_capacity: int
    emu_id: UUID | None

    def get_unit_type(self) -> UnitType:
        """Return COACH as the unit type."""
        return UnitType.COACH

    def is_motor_coach(self) -> bool:
        """
        Check if this coach has traction motors.

        Motor coaches are: MC1, MC2 (CSR) and M (Toshiba).

        Returns:
            True if this is a motor coach, False otherwise.
        """
        return self.coach_type in (CoachType.MC1, CoachType.MC2, CoachType.M)

    def is_trailer_coach(self) -> bool:
        """
        Check if this coach is a trailer (no traction).

        Trailer coaches are: R1, R2 (CSR) and R, RP (Toshiba).

        Returns:
            True if this is a trailer coach, False otherwise.
        """
        return not self.is_motor_coach()

    def _validate(self) -> None:
        """
        Validate coach-specific attributes.

        Raises:
            ValueError: If validation fails.
        """
        super()._validate()

        if self.seating_capacity <= 0:
            raise ValueError("seating_capacity must be positive")

        if self.is_motor_coach() and self.voltage is None:
            raise ValueError("Motor coaches must have voltage specified")

        if self.place is not None and self.place <= 0:
            raise ValueError("place must be a positive integer")
