"""
Coach type enumeration for railway coaches.

Defines the different types of coaches by manufacturer and function.
"""

from enum import Enum


class CoachType(Enum):
    """
    Type of coach by manufacturer and function.

    CSR (China South Rail) types:
        MC1: Motor Coach 1 with driver cabin (Coche Motriz con cabina 1).
        MC2: Motor Coach 2 with driver cabin (Coche Motriz con cabina 2).
        R1: Trailer coach (Remolque 1).
        R2: Trailer coach with pantograph (Remolque 2).

    Toshiba types:
        M: Motor coach (Motriz).
        R: Trailer coach with pantograph (Remolque).
        RP: Prima trailer coach (Remolque Prima / R').
    """

    # CSR types
    MC1 = "mc1"
    MC2 = "mc2"
    R1 = "r1"
    R2 = "r2"

    # Toshiba types
    M = "m"
    R = "r"
    RP = "rp"

    def __str__(self) -> str:
        """Return uppercase type name."""
        return self.value.upper()

    @property
    def is_motor(self) -> bool:
        """Check if this coach type has traction motors."""
        return self in (CoachType.MC1, CoachType.MC2, CoachType.M)

    @property
    def has_cabin(self) -> bool:
        """Check if this coach type has a driver cabin."""
        return self in (CoachType.MC1, CoachType.MC2)

    @property
    def has_pantograph(self) -> bool:
        """Check if this coach type typically has a pantograph."""
        # R2 (CSR) and R (Toshiba) have pantographs
        return self in (CoachType.R2, CoachType.R)

    @property
    def is_csr(self) -> bool:
        """Check if this is a CSR coach type."""
        return self in (CoachType.MC1, CoachType.MC2, CoachType.R1, CoachType.R2)

    @property
    def is_toshiba(self) -> bool:
        """Check if this is a Toshiba coach type."""
        return self in (CoachType.M, CoachType.R, CoachType.RP)
