"""
Pytest fixtures for domain entity tests.

Provides factory functions and fixtures for creating test entities.
"""

from datetime import date, datetime
from uuid import uuid4

import pytest

from core.domain.entities.coach import Coach
from core.domain.entities.emu import EMU
from core.domain.entities.emu_configuration import EmuConfiguration
from core.domain.entities.formation import Formation
from core.domain.value_objects.coach_type import CoachType
from core.domain.value_objects.unit_status import UnitStatus


def create_coach(
    coach_type: CoachType = CoachType.MC1,
    unit_number: str = "MC1-5001",
    manufacturer: str = "CSR Zhuzhou",
    voltage: int | None = 25000,
    has_pantograph: bool = False,
    has_cabin: bool = True,
    place: int | None = 1,
    seating_capacity: int = 52,
    emu_id=None,
    status: UnitStatus = UnitStatus.AVAILABLE,
    line: str | None = "LR",
) -> Coach:
    """Factory function to create a Coach with sensible defaults."""
    return Coach(
        id=uuid4(),
        unit_number=unit_number,
        description=f"Test {coach_type.value.upper()} Coach",
        manufacturer=manufacturer,
        manufacture_date=date(2014, 3, 15),
        commissioning_date=date(2015, 1, 20),
        status=status,
        line=line,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        coach_type=coach_type,
        voltage=voltage,
        has_pantograph=has_pantograph,
        has_cabin=has_cabin,
        place=place,
        seating_capacity=seating_capacity,
        emu_id=emu_id,
    )


def create_csr_4_coach_set(manufacturer: str = "CSR Zhuzhou") -> list[Coach]:
    """Create a standard CSR 4-coach set: [MC1, R1, R2, MC2]."""
    return [
        create_coach(
            coach_type=CoachType.MC1,
            unit_number="MC1-5001",
            manufacturer=manufacturer,
            voltage=25000,
            has_cabin=True,
            has_pantograph=False,
            place=1,
            seating_capacity=52,
        ),
        create_coach(
            coach_type=CoachType.R1,
            unit_number="R1-5601",
            manufacturer=manufacturer,
            voltage=None,
            has_cabin=False,
            has_pantograph=False,
            place=2,
            seating_capacity=72,
        ),
        create_coach(
            coach_type=CoachType.R2,
            unit_number="R2-5801",
            manufacturer=manufacturer,
            voltage=None,
            has_cabin=False,
            has_pantograph=True,
            place=3,
            seating_capacity=72,
        ),
        create_coach(
            coach_type=CoachType.MC2,
            unit_number="MC2-5002",
            manufacturer=manufacturer,
            voltage=25000,
            has_cabin=True,
            has_pantograph=False,
            place=4,
            seating_capacity=52,
        ),
    ]


def create_csr_3_coach_set(manufacturer: str = "CSR Zhuzhou") -> list[Coach]:
    """Create a CSR 3-coach set: [MC1, R1, MC2]."""
    return [
        create_coach(
            coach_type=CoachType.MC1,
            unit_number="MC1-5159",
            manufacturer=manufacturer,
            voltage=25000,
            has_cabin=True,
            place=1,
            seating_capacity=52,
        ),
        create_coach(
            coach_type=CoachType.R1,
            unit_number="R1-5680",
            manufacturer=manufacturer,
            voltage=None,
            has_cabin=False,
            place=2,
            seating_capacity=72,
        ),
        create_coach(
            coach_type=CoachType.MC2,
            unit_number="MC2-5160",
            manufacturer=manufacturer,
            voltage=25000,
            has_cabin=True,
            place=3,
            seating_capacity=52,
        ),
    ]


def create_toshiba_3_coach_set(manufacturer: str = "Toshiba") -> list[Coach]:
    """Create a Toshiba 3-coach set: [M, R, M]."""
    return [
        create_coach(
            coach_type=CoachType.M,
            unit_number="M4029",
            manufacturer=manufacturer,
            voltage=25000,
            has_cabin=True,
            has_pantograph=False,
            place=1,
            seating_capacity=48,
        ),
        create_coach(
            coach_type=CoachType.R,
            unit_number="R4615",
            manufacturer=manufacturer,
            voltage=None,
            has_cabin=False,
            has_pantograph=True,
            place=2,
            seating_capacity=68,
        ),
        create_coach(
            coach_type=CoachType.M,
            unit_number="M4030",
            manufacturer=manufacturer,
            voltage=25000,
            has_cabin=True,
            has_pantograph=False,
            place=3,
            seating_capacity=48,
        ),
    ]


def create_emu(
    unit_number: str = "M01",
    manufacturer: str = "CSR Zhuzhou",
    coaches: list[Coach] | None = None,
    voltage: int = 25000,
    max_speed: int = 120,
    total_passenger_capacity: int = 248,
    status: UnitStatus = UnitStatus.AVAILABLE,
    line: str | None = "LR",
    formation_id=None,
    configuration_id=None,
) -> EMU:
    """Factory function to create an EMU with sensible defaults."""
    if coaches is None:
        coaches = create_csr_4_coach_set(manufacturer)

    return EMU(
        id=uuid4(),
        unit_number=unit_number,
        description=f"Test EMU {unit_number}",
        manufacturer=manufacturer,
        manufacture_date=date(2014, 12, 1),
        commissioning_date=date(2015, 2, 1),
        status=status,
        line=line,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        voltage=voltage,
        max_speed=max_speed,
        total_passenger_capacity=total_passenger_capacity,
        coaches=coaches,
        formation_id=formation_id,
        configuration_id=configuration_id,
    )


def create_formation(
    f_id: str = "F120",
    unit_number: str = "F120",
    manufacturer: str = "CSR Zhuzhou",
    emus: list[EMU] | None = None,
    route: str | None = "Constitución - La Plata",
    status: UnitStatus = UnitStatus.AVAILABLE,
    line: str | None = "LR",
) -> Formation:
    """Factory function to create a Formation with sensible defaults."""
    if emus is None:
        emus = [create_emu(unit_number="M20", manufacturer=manufacturer)]

    return Formation(
        id=uuid4(),
        unit_number=unit_number,
        description=f"Test Formation {f_id}",
        manufacturer=manufacturer,
        manufacture_date=date(2014, 12, 1),
        commissioning_date=date(2015, 2, 1),
        status=status,
        line=line,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        f_id=f_id,
        emus=emus,
        route=route,
    )


def create_emu_configuration(
    name: str = "CSR-4",
    manufacturer: str = "CSR Zhuzhou",
    coach_sequence: tuple[CoachType, ...] = (
        CoachType.MC1,
        CoachType.R1,
        CoachType.R2,
        CoachType.MC2,
    ),
    min_coaches: int = 4,
    max_coaches: int = 4,
) -> EmuConfiguration:
    """Factory function to create an EmuConfiguration."""
    return EmuConfiguration(
        id=uuid4(),
        name=name,
        manufacturer=manufacturer,
        coach_sequence=coach_sequence,
        min_coaches=min_coaches,
        max_coaches=max_coaches,
    )


# Pytest fixtures


@pytest.fixture
def csr_motor_coach() -> Coach:
    """Create a CSR MC1 motor coach."""
    return create_coach(coach_type=CoachType.MC1)


@pytest.fixture
def csr_trailer_coach() -> Coach:
    """Create a CSR R1 trailer coach."""
    return create_coach(
        coach_type=CoachType.R1,
        unit_number="R1-5601",
        voltage=None,
        has_cabin=False,
        seating_capacity=72,
    )


@pytest.fixture
def csr_4_coach_set() -> list[Coach]:
    """Create a CSR 4-coach set."""
    return create_csr_4_coach_set()


@pytest.fixture
def csr_emu(csr_4_coach_set) -> EMU:
    """Create a CSR EMU with 4 coaches."""
    return create_emu(coaches=csr_4_coach_set)


@pytest.fixture
def csr_formation(csr_emu) -> Formation:
    """Create a CSR formation with 1 EMU."""
    return create_formation(emus=[csr_emu])


@pytest.fixture
def csr_4_config() -> EmuConfiguration:
    """Create a CSR 4-coach configuration."""
    return create_emu_configuration()
