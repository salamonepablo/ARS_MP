"""
Tests for EmuConfiguration entity.

Verifies EmuConfiguration creation, validation, and behavior.
"""

from uuid import uuid4

import pytest

from core.domain.entities.emu_configuration import EmuConfiguration
from core.domain.value_objects.coach_type import CoachType

from .conftest import (
    create_csr_3_coach_set,
    create_csr_4_coach_set,
    create_emu_configuration,
)


class TestEmuConfigurationCreation:
    """Tests for EmuConfiguration entity creation."""

    def test_create_csr_4_coach_configuration(self):
        """Se puede crear una configuración CSR de 4 coches."""
        config = create_emu_configuration(
            name="CSR-4",
            manufacturer="CSR Zhuzhou",
            coach_sequence=(CoachType.MC1, CoachType.R1, CoachType.R2, CoachType.MC2),
            min_coaches=4,
            max_coaches=4,
        )

        assert config.name == "CSR-4"
        assert config.manufacturer == "CSR Zhuzhou"
        assert len(config.coach_sequence) == 4
        assert config.min_coaches == 4
        assert config.max_coaches == 4

    def test_create_csr_3_coach_configuration(self):
        """Se puede crear una configuración CSR de 3 coches."""
        config = create_emu_configuration(
            name="CSR-3",
            manufacturer="CSR Zhuzhou",
            coach_sequence=(CoachType.MC1, CoachType.R1, CoachType.MC2),
            min_coaches=3,
            max_coaches=3,
        )

        assert config.name == "CSR-3"
        assert len(config.coach_sequence) == 3

    def test_create_toshiba_configuration(self):
        """Se puede crear una configuración Toshiba."""
        config = create_emu_configuration(
            name="Toshiba-3",
            manufacturer="Toshiba",
            coach_sequence=(CoachType.M, CoachType.R, CoachType.M),
            min_coaches=3,
            max_coaches=3,
        )

        assert config.name == "Toshiba-3"
        assert config.manufacturer == "Toshiba"
        assert CoachType.M in config.coach_sequence
        assert CoachType.R in config.coach_sequence

    def test_create_flexible_range_configuration(self):
        """Se puede crear una configuración con rango flexible."""
        config = create_emu_configuration(
            name="CSR-Flexible",
            min_coaches=3,
            max_coaches=4,
        )

        assert config.min_coaches == 3
        assert config.max_coaches == 4

    def test_configuration_is_immutable(self):
        """EmuConfiguration es inmutable (frozen)."""
        config = create_emu_configuration()

        with pytest.raises(AttributeError):
            config.name = "New Name"  # type: ignore


class TestEmuConfigurationValidation:
    """Tests for EmuConfiguration validation."""

    def test_min_coaches_must_be_positive(self):
        """min_coaches debe ser positivo."""
        with pytest.raises(ValueError, match="min_coaches must be positive"):
            EmuConfiguration(
                id=uuid4(),
                name="Invalid",
                manufacturer="CSR Zhuzhou",
                coach_sequence=(CoachType.MC1, CoachType.MC2),
                min_coaches=0,
                max_coaches=2,
            )

    def test_max_coaches_must_be_gte_min_coaches(self):
        """max_coaches debe ser >= min_coaches."""
        with pytest.raises(ValueError, match="max_coaches must be >= min_coaches"):
            EmuConfiguration(
                id=uuid4(),
                name="Invalid",
                manufacturer="CSR Zhuzhou",
                coach_sequence=(CoachType.MC1, CoachType.MC2),
                min_coaches=4,
                max_coaches=3,  # Menor que min
            )

    def test_name_cannot_be_empty(self):
        """name no puede estar vacío."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            EmuConfiguration(
                id=uuid4(),
                name="",
                manufacturer="CSR Zhuzhou",
                coach_sequence=(CoachType.MC1, CoachType.MC2),
                min_coaches=2,
                max_coaches=2,
            )

    def test_name_cannot_be_whitespace(self):
        """name no puede ser solo espacios."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            EmuConfiguration(
                id=uuid4(),
                name="   ",
                manufacturer="CSR Zhuzhou",
                coach_sequence=(CoachType.MC1, CoachType.MC2),
                min_coaches=2,
                max_coaches=2,
            )


class TestEmuConfigurationBehavior:
    """Tests for EmuConfiguration behavior methods."""

    def test_validate_accepts_valid_coach_count(self):
        """validate() acepta cantidad válida de coches."""
        config = create_emu_configuration(
            min_coaches=4,
            max_coaches=4,
        )
        coaches = create_csr_4_coach_set()

        # Should not raise
        config.validate(coaches)

    def test_validate_rejects_too_few_coaches(self):
        """validate() rechaza muy pocos coches."""
        config = create_emu_configuration(
            min_coaches=4,
            max_coaches=4,
        )
        coaches = create_csr_3_coach_set()  # Only 3 coaches

        with pytest.raises(ValueError, match="Coach count .* outside configuration range"):
            config.validate(coaches)

    def test_validate_rejects_too_many_coaches(self):
        """validate() rechaza demasiados coches."""
        config = create_emu_configuration(
            min_coaches=2,
            max_coaches=3,
        )
        coaches = create_csr_4_coach_set()  # 4 coaches, max is 3

        with pytest.raises(ValueError, match="Coach count .* outside configuration range"):
            config.validate(coaches)

    def test_validate_accepts_flexible_range(self):
        """validate() acepta rango flexible."""
        config = create_emu_configuration(
            min_coaches=3,
            max_coaches=4,
        )

        # 3 coaches should be valid
        coaches_3 = create_csr_3_coach_set()
        config.validate(coaches_3)  # Should not raise

        # 4 coaches should also be valid
        coaches_4 = create_csr_4_coach_set()
        config.validate(coaches_4)  # Should not raise

    def test_matches_sequence_exact_match(self):
        """matches_sequence() retorna True para secuencia exacta."""
        config = create_emu_configuration(
            coach_sequence=(CoachType.MC1, CoachType.R1, CoachType.R2, CoachType.MC2),
        )
        coaches = create_csr_4_coach_set()

        assert config.matches_sequence(coaches) is True

    def test_matches_sequence_wrong_order(self):
        """matches_sequence() retorna False para secuencia incorrecta."""
        config = create_emu_configuration(
            coach_sequence=(CoachType.MC1, CoachType.R1, CoachType.R2, CoachType.MC2),
        )
        # Create coaches in wrong order
        coaches = create_csr_4_coach_set()
        coaches_reversed = list(reversed(coaches))

        assert config.matches_sequence(coaches_reversed) is False

    def test_matches_sequence_wrong_count(self):
        """matches_sequence() retorna False para cantidad incorrecta."""
        config = create_emu_configuration(
            coach_sequence=(CoachType.MC1, CoachType.R1, CoachType.R2, CoachType.MC2),
            min_coaches=4,
            max_coaches=4,
        )
        coaches = create_csr_3_coach_set()  # 3 coaches, sequence expects 4

        assert config.matches_sequence(coaches) is False


class TestEmuConfigurationRealWorld:
    """Tests for real-world EmuConfiguration scenarios."""

    def test_csr_standard_configurations(self):
        """Configuraciones estándar CSR."""
        # CSR 4-coach: [MC1, R1, R2, MC2]
        config_4 = EmuConfiguration(
            id=uuid4(),
            name="CSR-4-Standard",
            manufacturer="CSR Zhuzhou",
            coach_sequence=(CoachType.MC1, CoachType.R1, CoachType.R2, CoachType.MC2),
            min_coaches=4,
            max_coaches=4,
        )

        # CSR 3-coach: [MC1, R1, MC2] - for M80, M82, etc.
        config_3 = EmuConfiguration(
            id=uuid4(),
            name="CSR-3-Standard",
            manufacturer="CSR Zhuzhou",
            coach_sequence=(CoachType.MC1, CoachType.R1, CoachType.MC2),
            min_coaches=3,
            max_coaches=3,
        )

        assert len(config_4.coach_sequence) == 4
        assert len(config_3.coach_sequence) == 3

    def test_toshiba_configurations(self):
        """Configuraciones Toshiba."""
        # Toshiba 3-coach: [M, R, M]
        config_3 = EmuConfiguration(
            id=uuid4(),
            name="Toshiba-3-Standard",
            manufacturer="Toshiba",
            coach_sequence=(CoachType.M, CoachType.R, CoachType.M),
            min_coaches=3,
            max_coaches=3,
        )

        # Toshiba 4-coach: [M, R, RP, M]
        config_4 = EmuConfiguration(
            id=uuid4(),
            name="Toshiba-4-Standard",
            manufacturer="Toshiba",
            coach_sequence=(CoachType.M, CoachType.R, CoachType.RP, CoachType.M),
            min_coaches=4,
            max_coaches=4,
        )

        assert CoachType.M in config_3.coach_sequence
        assert CoachType.RP in config_4.coach_sequence
