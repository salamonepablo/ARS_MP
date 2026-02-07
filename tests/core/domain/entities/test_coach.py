"""
Tests for Coach entity.

Verifies coach creation, validation, and behavior.
"""

from datetime import date, datetime
from uuid import uuid4

import pytest

from core.domain.entities.coach import Coach
from core.domain.value_objects.coach_type import CoachType
from core.domain.value_objects.unit_type import UnitType

from .conftest import create_coach


class TestCoachCreation:
    """Tests for Coach entity creation."""

    def test_create_motor_coach_csr(self):
        """Se puede crear un coche motor CSR."""
        coach = create_coach(
            coach_type=CoachType.MC1,
            unit_number="MC1-5001",
            voltage=25000,
            has_cabin=True,
        )

        assert coach.unit_number == "MC1-5001"
        assert coach.coach_type == CoachType.MC1
        assert coach.voltage == 25000
        assert coach.is_motor_coach() is True
        assert coach.has_cabin is True
        assert coach.get_unit_type() == UnitType.COACH

    def test_create_trailer_coach_csr(self):
        """Se puede crear un coche remolque CSR."""
        coach = create_coach(
            coach_type=CoachType.R1,
            unit_number="R1-5601",
            voltage=None,
            has_cabin=False,
            has_pantograph=False,
            seating_capacity=72,
        )

        assert coach.unit_number == "R1-5601"
        assert coach.coach_type == CoachType.R1
        assert coach.voltage is None
        assert coach.is_motor_coach() is False
        assert coach.is_trailer_coach() is True
        assert coach.has_cabin is False

    def test_create_trailer_coach_with_pantograph(self):
        """Se puede crear un coche remolque R2 con pantógrafo."""
        coach = create_coach(
            coach_type=CoachType.R2,
            unit_number="R2-5801",
            voltage=None,
            has_cabin=False,
            has_pantograph=True,
            seating_capacity=72,
        )

        assert coach.has_pantograph is True
        assert coach.is_trailer_coach() is True

    def test_create_toshiba_motor_coach(self):
        """Se puede crear un coche motor Toshiba."""
        coach = create_coach(
            coach_type=CoachType.M,
            unit_number="M4029",
            manufacturer="Toshiba",
            voltage=25000,
            has_cabin=True,
            seating_capacity=48,
        )

        assert coach.manufacturer == "Toshiba"
        assert coach.coach_type == CoachType.M
        assert coach.is_motor_coach() is True

    def test_create_toshiba_trailer_coach_rp(self):
        """Se puede crear un coche remolque prima Toshiba (RP)."""
        coach = create_coach(
            coach_type=CoachType.RP,
            unit_number="RP4822",
            manufacturer="Toshiba",
            voltage=None,
            has_cabin=False,
            has_pantograph=False,
            seating_capacity=64,
        )

        assert coach.coach_type == CoachType.RP
        assert coach.is_trailer_coach() is True


class TestCoachValidation:
    """Tests for Coach validation rules."""

    def test_motor_coach_requires_voltage(self):
        """Coches motrices deben tener voltage."""
        with pytest.raises(ValueError, match="Motor coaches must have voltage"):
            create_coach(
                coach_type=CoachType.MC1,
                voltage=None,  # Error: motor coach sin voltage
            )

    def test_trailer_coach_without_voltage_is_valid(self):
        """Coches remolque no necesitan voltage."""
        coach = create_coach(
            coach_type=CoachType.R1,
            voltage=None,
        )
        assert coach.voltage is None

    def test_seating_capacity_must_be_positive(self):
        """Capacidad de asientos debe ser positiva."""
        with pytest.raises(ValueError, match="seating_capacity must be positive"):
            create_coach(seating_capacity=0)

    def test_negative_seating_capacity_rejected(self):
        """Capacidad negativa rechazada."""
        with pytest.raises(ValueError, match="seating_capacity must be positive"):
            create_coach(seating_capacity=-10)

    def test_place_must_be_positive_if_provided(self):
        """Posición debe ser positiva si se especifica."""
        with pytest.raises(ValueError, match="place must be a positive integer"):
            create_coach(place=0)

    def test_place_none_is_valid(self):
        """Posición puede ser None."""
        coach = create_coach(place=None)
        assert coach.place is None

    def test_empty_unit_number_rejected(self):
        """Número de unidad vacío rechazado."""
        with pytest.raises(ValueError, match="unit_number cannot be empty"):
            create_coach(unit_number="")

    def test_whitespace_unit_number_rejected(self):
        """Número de unidad solo espacios rechazado."""
        with pytest.raises(ValueError, match="unit_number cannot be empty"):
            create_coach(unit_number="   ")

    def test_commissioning_date_in_future_rejected(self):
        """Fecha de puesta en servicio futura rechazada."""
        from datetime import timedelta

        future_date = date.today() + timedelta(days=30)

        with pytest.raises(ValueError, match="commissioning_date cannot be in the future"):
            Coach(
                id=uuid4(),
                unit_number="MC1-5001",
                description="Test Coach",
                manufacturer="CSR Zhuzhou",
                manufacture_date=None,
                commissioning_date=future_date,
                line="LR",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                coach_type=CoachType.MC1,
                voltage=25000,
                has_pantograph=False,
                has_cabin=True,
                place=1,
                seating_capacity=52,
                emu_id=None,
            )

    def test_manufacture_date_after_commissioning_rejected(self):
        """Fecha de fabricación posterior a puesta en servicio rechazada."""
        with pytest.raises(
            ValueError, match="manufacture_date must be before commissioning_date"
        ):
            Coach(
                id=uuid4(),
                unit_number="MC1-5001",
                description="Test Coach",
                manufacturer="CSR Zhuzhou",
                manufacture_date=date(2016, 1, 1),  # Después de commissioning
                commissioning_date=date(2015, 1, 1),
                line="LR",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                coach_type=CoachType.MC1,
                voltage=25000,
                has_pantograph=False,
                has_cabin=True,
                place=1,
                seating_capacity=52,
                emu_id=None,
            )


class TestCoachBehavior:
    """Tests for Coach behavior methods."""

    def test_is_motor_coach_for_mc1(self):
        """MC1 es coche motor."""
        coach = create_coach(coach_type=CoachType.MC1)
        assert coach.is_motor_coach() is True
        assert coach.is_trailer_coach() is False

    def test_is_motor_coach_for_mc2(self):
        """MC2 es coche motor."""
        coach = create_coach(coach_type=CoachType.MC2, unit_number="MC2-5002")
        assert coach.is_motor_coach() is True

    def test_is_motor_coach_for_toshiba_m(self):
        """Toshiba M es coche motor."""
        coach = create_coach(
            coach_type=CoachType.M,
            manufacturer="Toshiba",
            unit_number="M4029",
        )
        assert coach.is_motor_coach() is True

    def test_is_trailer_coach_for_r1(self):
        """R1 es coche remolque."""
        coach = create_coach(coach_type=CoachType.R1, voltage=None, unit_number="R1-5601")
        assert coach.is_trailer_coach() is True
        assert coach.is_motor_coach() is False

    def test_is_trailer_coach_for_r2(self):
        """R2 es coche remolque."""
        coach = create_coach(coach_type=CoachType.R2, voltage=None, unit_number="R2-5801")
        assert coach.is_trailer_coach() is True

    def test_is_trailer_coach_for_toshiba_r(self):
        """Toshiba R es coche remolque."""
        coach = create_coach(
            coach_type=CoachType.R,
            manufacturer="Toshiba",
            voltage=None,
            unit_number="R4615",
        )
        assert coach.is_trailer_coach() is True

    def test_is_trailer_coach_for_toshiba_rp(self):
        """Toshiba RP es coche remolque."""
        coach = create_coach(
            coach_type=CoachType.RP,
            manufacturer="Toshiba",
            voltage=None,
            unit_number="RP4822",
        )
        assert coach.is_trailer_coach() is True

    def test_get_unit_type_returns_coach(self):
        """get_unit_type() retorna COACH."""
        coach = create_coach()
        assert coach.get_unit_type() == UnitType.COACH
