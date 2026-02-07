"""
Tests for EMU entity.

Verifies EMU creation, composition validation, and behavior.
"""

import pytest

from core.domain.value_objects.coach_type import CoachType
from core.domain.value_objects.unit_status import UnitStatus
from core.domain.value_objects.unit_type import UnitType

from .conftest import (
    create_coach,
    create_csr_3_coach_set,
    create_csr_4_coach_set,
    create_emu,
    create_emu_configuration,
    create_toshiba_3_coach_set,
)


class TestEmuCreation:
    """Tests for EMU entity creation."""

    def test_create_valid_csr_emu_4_coaches(self):
        """Se puede crear una EMU CSR válida con 4 coches."""
        coaches = create_csr_4_coach_set()
        emu = create_emu(
            unit_number="M01",
            coaches=coaches,
            total_passenger_capacity=248,
        )

        assert emu.unit_number == "M01"
        assert len(emu.coaches) == 4
        assert emu.voltage == 25000
        assert emu.max_speed == 120
        assert emu.get_unit_type() == UnitType.EMU

    def test_create_valid_csr_emu_3_coaches(self):
        """Se puede crear una EMU CSR válida con 3 coches (M80, M82, etc.)."""
        coaches = create_csr_3_coach_set()
        emu = create_emu(
            unit_number="M80",
            coaches=coaches,
            total_passenger_capacity=176,
        )

        assert len(emu.coaches) == 3
        assert emu.get_coach_count() == 3

    def test_create_valid_toshiba_emu(self):
        """Se puede crear una EMU Toshiba válida."""
        coaches = create_toshiba_3_coach_set()
        emu = create_emu(
            unit_number="T15",
            manufacturer="Toshiba",
            coaches=coaches,
            total_passenger_capacity=164,
        )

        assert emu.unit_number == "T15"
        assert emu.manufacturer == "Toshiba"
        assert len(emu.coaches) == 3

    def test_emu_with_optional_formation_id(self):
        """EMU puede tener formation_id opcional."""
        from uuid import uuid4

        formation_id = uuid4()
        emu = create_emu(formation_id=formation_id)

        assert emu.formation_id == formation_id

    def test_emu_without_formation_id(self):
        """EMU puede existir sin formation_id."""
        emu = create_emu(formation_id=None)
        assert emu.formation_id is None


class TestEmuValidation:
    """Tests for EMU composition validation."""

    def test_emu_must_have_at_least_2_coaches(self):
        """EMU debe tener al menos 2 coches."""
        single_coach = [create_coach()]

        with pytest.raises(ValueError, match="EMU must have at least 2 coaches"):
            create_emu(coaches=single_coach)

    def test_emu_with_empty_coaches_rejected(self):
        """EMU sin coches rechazada."""
        with pytest.raises(ValueError, match="EMU must have at least 2 coaches"):
            create_emu(coaches=[])

    def test_emu_coaches_must_be_same_manufacturer(self):
        """Todos los coches de una EMU deben ser del mismo fabricante."""
        mixed_coaches = [
            create_coach(
                coach_type=CoachType.MC1,
                manufacturer="CSR Zhuzhou",
                unit_number="MC1-5001",
            ),
            create_coach(
                coach_type=CoachType.M,
                manufacturer="Toshiba",  # Diferente fabricante
                unit_number="M4029",
            ),
        ]

        with pytest.raises(ValueError, match="All coaches must be from same manufacturer"):
            create_emu(coaches=mixed_coaches)

    def test_emu_with_2_coaches_is_valid(self):
        """EMU con exactamente 2 coches es válida."""
        two_coaches = [
            create_coach(
                coach_type=CoachType.MC1,
                unit_number="MC1-5001",
            ),
            create_coach(
                coach_type=CoachType.MC2,
                unit_number="MC2-5002",
            ),
        ]

        emu = create_emu(coaches=two_coaches)
        assert len(emu.coaches) == 2


class TestEmuBehavior:
    """Tests for EMU behavior methods."""

    def test_get_motor_coaches(self):
        """get_motor_coaches() retorna solo coches motrices."""
        coaches = create_csr_4_coach_set()  # [MC1, R1, R2, MC2]
        emu = create_emu(coaches=coaches)

        motor_coaches = emu.get_motor_coaches()

        assert len(motor_coaches) == 2
        assert all(c.is_motor_coach() for c in motor_coaches)
        coach_types = {c.coach_type for c in motor_coaches}
        assert coach_types == {CoachType.MC1, CoachType.MC2}

    def test_get_trailer_coaches(self):
        """get_trailer_coaches() retorna solo coches remolque."""
        coaches = create_csr_4_coach_set()  # [MC1, R1, R2, MC2]
        emu = create_emu(coaches=coaches)

        trailer_coaches = emu.get_trailer_coaches()

        assert len(trailer_coaches) == 2
        assert all(c.is_trailer_coach() for c in trailer_coaches)
        coach_types = {c.coach_type for c in trailer_coaches}
        assert coach_types == {CoachType.R1, CoachType.R2}

    def test_get_coach_count(self):
        """get_coach_count() retorna número de coches."""
        coaches = create_csr_4_coach_set()
        emu = create_emu(coaches=coaches)

        assert emu.get_coach_count() == 4

    def test_get_coach_count_3_coach_emu(self):
        """get_coach_count() para EMU de 3 coches."""
        coaches = create_csr_3_coach_set()
        emu = create_emu(coaches=coaches)

        assert emu.get_coach_count() == 3

    def test_get_unit_type_returns_emu(self):
        """get_unit_type() retorna EMU."""
        emu = create_emu()
        assert emu.get_unit_type() == UnitType.EMU

    def test_is_available_when_status_available(self):
        """EMU disponible cuando status es AVAILABLE."""
        emu = create_emu(status=UnitStatus.AVAILABLE)
        assert emu.is_available() is True

    def test_is_not_available_when_in_maintenance(self):
        """EMU no disponible cuando está en mantenimiento."""
        emu = create_emu(status=UnitStatus.IN_MAINTENANCE)
        assert emu.is_available() is False

    def test_is_in_workshop_when_under_repair(self):
        """EMU en taller cuando está en reparación."""
        emu = create_emu(status=UnitStatus.UNDER_REPAIR)
        assert emu.is_in_workshop() is True


class TestEmuConfiguration:
    """Tests for EMU configuration validation."""

    def test_validate_configuration_valid_coaches(self):
        """validate_configuration() acepta coches válidos."""
        config = create_emu_configuration(
            name="CSR-4",
            min_coaches=4,
            max_coaches=4,
        )
        coaches = create_csr_4_coach_set()
        emu = create_emu(coaches=coaches)

        # Should not raise
        emu.validate_configuration(config)

    def test_validate_configuration_rejects_wrong_count(self):
        """validate_configuration() rechaza cantidad incorrecta de coches."""
        config = create_emu_configuration(
            name="CSR-4",
            min_coaches=4,
            max_coaches=4,
        )
        # EMU with only 3 coaches
        coaches = create_csr_3_coach_set()
        emu = create_emu(coaches=coaches)

        with pytest.raises(ValueError, match="Coach count .* outside configuration range"):
            emu.validate_configuration(config)

    def test_validate_configuration_accepts_flexible_range(self):
        """validate_configuration() acepta rango flexible."""
        config = create_emu_configuration(
            name="CSR-Flexible",
            min_coaches=3,
            max_coaches=4,
        )

        # 3-coach EMU should be valid
        coaches_3 = create_csr_3_coach_set()
        emu_3 = create_emu(coaches=coaches_3)
        emu_3.validate_configuration(config)  # Should not raise

        # 4-coach EMU should also be valid
        coaches_4 = create_csr_4_coach_set()
        emu_4 = create_emu(coaches=coaches_4)
        emu_4.validate_configuration(config)  # Should not raise
