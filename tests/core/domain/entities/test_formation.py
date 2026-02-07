"""
Tests for Formation entity.

Verifies Formation creation, composition validation, and behavior.
"""

import pytest

from core.domain.value_objects.unit_type import UnitType

from .conftest import (
    create_csr_3_coach_set,
    create_csr_4_coach_set,
    create_emu,
    create_formation,
    create_toshiba_3_coach_set,
)


class TestFormationCreation:
    """Tests for Formation entity creation."""

    def test_create_valid_formation_single_emu(self):
        """Se puede crear una formación válida con 1 EMU."""
        emu = create_emu(unit_number="M80", coaches=create_csr_3_coach_set())
        formation = create_formation(
            f_id="F250",
            unit_number="F250",
            emus=[emu],
            route="Constitución - La Plata",
        )

        assert formation.f_id == "F250"
        assert formation.unit_number == "F250"
        assert len(formation.emus) == 1
        assert formation.route == "Constitución - La Plata"
        assert formation.get_unit_type() == UnitType.FORMATION

    def test_create_valid_formation_two_emus(self):
        """Se puede crear una formación válida con 2 EMUs."""
        emu1 = create_emu(
            unit_number="M20",
            coaches=create_csr_3_coach_set(),
            total_passenger_capacity=176,
        )
        emu2 = create_emu(
            unit_number="M45",
            coaches=create_csr_4_coach_set(),
            total_passenger_capacity=248,
        )

        formation = create_formation(
            f_id="F120",
            unit_number="F120",
            emus=[emu1, emu2],
        )

        assert len(formation.emus) == 2
        assert formation.get_emu_count() == 2

    def test_create_formation_with_optional_route(self):
        """Formación puede tener route opcional."""
        formation = create_formation(route=None)
        assert formation.route is None

    def test_create_formation_with_route(self):
        """Formación puede tener route especificado."""
        formation = create_formation(route="Bosques - Temperley")
        assert formation.route == "Bosques - Temperley"


class TestFormationValidation:
    """Tests for Formation validation rules."""

    def test_formation_must_have_at_least_one_emu(self):
        """Formación debe tener al menos 1 EMU."""
        with pytest.raises(ValueError, match="Formation must have at least 1 EMU"):
            create_formation(emus=[])

    def test_formation_emus_must_be_same_manufacturer(self):
        """Ambos EMUs de una formación deben ser del mismo fabricante."""
        emu_csr = create_emu(
            unit_number="M20",
            manufacturer="CSR Zhuzhou",
            coaches=create_csr_4_coach_set("CSR Zhuzhou"),
        )
        emu_toshiba = create_emu(
            unit_number="T15",
            manufacturer="Toshiba",
            coaches=create_toshiba_3_coach_set("Toshiba"),
        )

        with pytest.raises(ValueError, match="All EMUs must be from same manufacturer"):
            create_formation(emus=[emu_csr, emu_toshiba])

    def test_formation_same_manufacturer_is_valid(self):
        """Formación con EMUs del mismo fabricante es válida."""
        emu1 = create_emu(
            unit_number="M20",
            manufacturer="CSR Zhuzhou",
        )
        emu2 = create_emu(
            unit_number="M45",
            manufacturer="CSR Zhuzhou",
        )

        formation = create_formation(
            manufacturer="CSR Zhuzhou",
            emus=[emu1, emu2],
        )

        assert len(formation.emus) == 2


class TestFormationBehavior:
    """Tests for Formation behavior methods."""

    def test_get_total_coaches_single_emu(self):
        """get_total_coaches() para formación con 1 EMU."""
        emu = create_emu(coaches=create_csr_4_coach_set())  # 4 coaches
        formation = create_formation(emus=[emu])

        assert formation.get_total_coaches() == 4

    def test_get_total_coaches_two_emus(self):
        """get_total_coaches() para formación con 2 EMUs."""
        emu1 = create_emu(
            unit_number="M01",
            coaches=create_csr_3_coach_set(),
        )  # 3 coaches
        emu2 = create_emu(
            unit_number="M20",
            coaches=create_csr_4_coach_set(),
        )  # 4 coaches

        formation = create_formation(emus=[emu1, emu2])

        assert formation.get_total_coaches() == 7

    def test_get_all_coaches(self):
        """get_all_coaches() retorna todos los coches de todos los EMUs."""
        coaches1 = create_csr_3_coach_set()  # 3 coaches
        coaches2 = create_csr_4_coach_set()  # 4 coaches

        emu1 = create_emu(unit_number="M80", coaches=coaches1)
        emu2 = create_emu(unit_number="M01", coaches=coaches2)

        formation = create_formation(emus=[emu1, emu2])

        all_coaches = formation.get_all_coaches()

        assert len(all_coaches) == 7
        # Verify all coaches from both EMUs are present
        assert coaches1[0] in all_coaches
        assert coaches2[0] in all_coaches

    def test_get_total_passenger_capacity_single_emu(self):
        """get_total_passenger_capacity() para formación con 1 EMU."""
        emu = create_emu(total_passenger_capacity=248)
        formation = create_formation(emus=[emu])

        assert formation.get_total_passenger_capacity() == 248

    def test_get_total_passenger_capacity_two_emus(self):
        """get_total_passenger_capacity() para formación con 2 EMUs."""
        emu1 = create_emu(
            unit_number="M80",
            coaches=create_csr_3_coach_set(),
            total_passenger_capacity=176,
        )
        emu2 = create_emu(
            unit_number="M01",
            coaches=create_csr_4_coach_set(),
            total_passenger_capacity=248,
        )

        formation = create_formation(emus=[emu1, emu2])

        assert formation.get_total_passenger_capacity() == 424

    def test_get_emu_count(self):
        """get_emu_count() retorna número de EMUs."""
        emu1 = create_emu(unit_number="M20")
        emu2 = create_emu(unit_number="M45")

        formation = create_formation(emus=[emu1, emu2])

        assert formation.get_emu_count() == 2

    def test_get_unit_type_returns_formation(self):
        """get_unit_type() retorna FORMATION."""
        formation = create_formation()
        assert formation.get_unit_type() == UnitType.FORMATION


class TestFormationRealWorldScenarios:
    """Tests for real-world Formation scenarios from Línea Roca."""

    def test_formation_f120_two_csr_emus(self):
        """Ejemplo real: F120 con EMUs M20 y M45."""
        # M20: 3-coach EMU
        emu_m20 = create_emu(
            unit_number="M20",
            manufacturer="CSR Zhuzhou",
            coaches=create_csr_3_coach_set(),
            total_passenger_capacity=176,
        )
        # M45: 4-coach EMU
        emu_m45 = create_emu(
            unit_number="M45",
            manufacturer="CSR Zhuzhou",
            coaches=create_csr_4_coach_set(),
            total_passenger_capacity=248,
        )

        formation = create_formation(
            f_id="F120",
            unit_number="F120",
            manufacturer="CSR Zhuzhou",
            emus=[emu_m20, emu_m45],
            route="Constitución - La Plata",
            line="LR",
        )

        assert formation.f_id == "F120"
        assert formation.get_emu_count() == 2
        assert formation.get_total_coaches() == 7
        assert formation.get_total_passenger_capacity() == 424
        assert formation.line == "LR"

    def test_formation_f250_single_emu(self):
        """Ejemplo real: F250 con una sola EMU M80."""
        emu_m80 = create_emu(
            unit_number="M80",
            manufacturer="CSR Zhuzhou",
            coaches=create_csr_3_coach_set(),
            total_passenger_capacity=176,
        )

        formation = create_formation(
            f_id="F250",
            unit_number="F250",
            manufacturer="CSR Zhuzhou",
            emus=[emu_m80],
            route="Bosques - Temperley",
        )

        assert formation.f_id == "F250"
        assert formation.get_emu_count() == 1
        assert formation.get_total_coaches() == 3
