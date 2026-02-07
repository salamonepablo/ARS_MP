"""
Base entity for all railway maintenance units.

This abstract base class defines the common attributes and behavior
for all maintenance units in the railway system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID

from core.domain.value_objects.unit_type import UnitType


@dataclass(kw_only=True)
class MaintenanceUnit(ABC):
    """
    Base entity for all railway maintenance units.

    Can represent formations (complete trains), EMUs (electric multiple units),
    or individual coaches. All share common attributes for identification
    and lifecycle tracking.

    Attributes:
        id: Unique identifier (UUID).
        unit_number: Human-readable unit number (e.g., "M01", "MC1-5001").
        description: Descriptive text about the unit.
        manufacturer: Name of manufacturer (e.g., "CSR Zhuzhou", "Toshiba").
        manufacture_date: Date the unit was manufactured (optional).
        commissioning_date: Date the unit entered service.
        line: Railway line identifier (e.g., "LR" for Línea Roca).
        created_at: Timestamp of record creation.
        updated_at: Timestamp of last record update.

    Raises:
        ValueError: If unit_number is empty, commissioning_date is in future,
            or manufacture_date is after commissioning_date.
    """

    id: UUID
    unit_number: str
    description: str
    manufacturer: str
    manufacture_date: date | None
    commissioning_date: date
    line: str | None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @abstractmethod
    def get_unit_type(self) -> UnitType:
        """
        Return the type of this unit.

        Returns:
            UnitType enum value indicating the unit type.
        """
        pass

    def __post_init__(self) -> None:
        """Validate unit data after initialization."""
        self._validate()

    def _validate(self) -> None:
        """
        Validate common unit attributes.

        Raises:
            ValueError: If validation fails.
        """
        if not self.unit_number or not self.unit_number.strip():
            raise ValueError("unit_number cannot be empty")

        if self.commissioning_date > date.today():
            raise ValueError("commissioning_date cannot be in the future")

        if (
            self.manufacture_date is not None
            and self.manufacture_date > self.commissioning_date
        ):
            raise ValueError("manufacture_date must be before commissioning_date")
