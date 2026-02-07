"""
EMU Configuration entity defining valid coach compositions.

Represents the allowed coach sequences for different EMU types.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from core.domain.value_objects.coach_type import CoachType

if TYPE_CHECKING:
    from core.domain.entities.coach import Coach


@dataclass(frozen=True)
class EmuConfiguration:
    """
    Defines a valid coach composition for an EMU.

    This immutable configuration specifies the valid sequence and count
    of coaches for a particular EMU type. Used to validate EMU compositions.

    Examples:
        CSR 4-coach: [MC1, R1, R2, MC2]
        CSR 3-coach: [MC1, R1, MC2]
        Toshiba 4-coach: [M, R, RP, M]
        Toshiba 3-coach: [M, R, M]

    Attributes:
        id: Unique identifier.
        name: Configuration name (e.g., "CSR-4", "Toshiba-3").
        manufacturer: Manufacturer name.
        coach_sequence: Ordered list of expected coach types.
        min_coaches: Minimum number of coaches allowed.
        max_coaches: Maximum number of coaches allowed.
    """

    id: UUID
    name: str
    manufacturer: str
    coach_sequence: tuple[CoachType, ...]  # Use tuple for immutability
    min_coaches: int
    max_coaches: int

    def validate(self, coaches: list["Coach"]) -> None:
        """
        Validate if a coach list matches this configuration.

        Checks that the number of coaches is within the allowed range.
        Optionally can validate the sequence order (not implemented yet).

        Args:
            coaches: List of Coach entities to validate.

        Raises:
            ValueError: If coach count is outside configuration range.
        """
        coach_count = len(coaches)
        if coach_count < self.min_coaches or coach_count > self.max_coaches:
            raise ValueError(
                f"Coach count {coach_count} outside configuration range "
                f"[{self.min_coaches}, {self.max_coaches}]"
            )

    def matches_sequence(self, coaches: list["Coach"]) -> bool:
        """
        Check if coaches match the expected sequence exactly.

        Args:
            coaches: List of Coach entities to check.

        Returns:
            True if coaches match the sequence, False otherwise.
        """
        if len(coaches) != len(self.coach_sequence):
            return False

        return all(
            coach.coach_type == expected_type
            for coach, expected_type in zip(coaches, self.coach_sequence)
        )

    def __post_init__(self) -> None:
        """Validate configuration attributes."""
        if self.min_coaches <= 0:
            raise ValueError("min_coaches must be positive")
        if self.max_coaches < self.min_coaches:
            raise ValueError("max_coaches must be >= min_coaches")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
