"""
Formation entity representing an operational train formation.

A formation is one or more EMUs operating together as a complete train.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.domain.entities.maintenance_unit import MaintenanceUnit
from core.domain.value_objects.unit_type import UnitType

if TYPE_CHECKING:
    from core.domain.entities.coach import Coach
    from core.domain.entities.emu import EMU


@dataclass(kw_only=True)
class Formation(MaintenanceUnit):
    """
    Formation: operational unit composed of one or more EMUs.

    Represents a complete trainset that operates together in service.
    Example sizes: 1 EMU (3-4 coaches) or 2 EMUs (6-8 coaches total).

    Examples:
        F120 = (EMU M20, EMU M45) - Two EMUs operating together
        F152 = (EMU M71, EMU M37)
        F250 = (EMU M80) - Single EMU formation

    Attributes:
        f_id: Formation identifier (e.g., "F120", "F152").
        emus: List of EMUs composing this formation.
        route: Route/service information (e.g., "Constitución - La Plata").

    Raises:
        ValueError: If formation has no EMUs, or EMUs are from
            different manufacturers.
    """

    f_id: str
    emus: list["EMU"] = field(default_factory=list)
    route: str | None = None

    def get_unit_type(self) -> UnitType:
        """Return FORMATION as the unit type."""
        return UnitType.FORMATION

    def __post_init__(self) -> None:
        """Validate formation data after initialization."""
        super().__post_init__()
        self._validate_composition()

    def _validate_composition(self) -> None:
        """
        Validate that formation has at least 1 EMU.

        Raises:
            ValueError: If composition is invalid.
        """
        if len(self.emus) < 1:
            raise ValueError("Formation must have at least 1 EMU")

        # Verify all EMUs are from the same manufacturer
        if self.emus:
            manufacturers = {emu.manufacturer for emu in self.emus}
            if len(manufacturers) > 1:
                raise ValueError("All EMUs must be from same manufacturer")

    def get_total_coaches(self) -> int:
        """
        Return total number of coaches in formation.

        Returns:
            Sum of coaches across all EMUs.
        """
        return sum(len(emu.coaches) for emu in self.emus)

    def get_all_coaches(self) -> list["Coach"]:
        """
        Return all coaches from all EMUs.

        Returns:
            Flat list of all coaches in the formation.
        """
        all_coaches: list["Coach"] = []
        for emu in self.emus:
            all_coaches.extend(emu.coaches)
        return all_coaches

    def get_total_passenger_capacity(self) -> int:
        """
        Return combined passenger capacity of all EMUs.

        Returns:
            Total passenger capacity.
        """
        return sum(emu.total_passenger_capacity for emu in self.emus)

    def get_emu_count(self) -> int:
        """Return the number of EMUs in this formation."""
        return len(self.emus)
