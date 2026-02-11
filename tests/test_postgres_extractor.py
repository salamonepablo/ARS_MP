"""
Tests for postgres_extractor helper functions and integration tests.

Tests cover:
- Helper functions: normalize_module_id, determine_fleet_type, etc.
- Integration tests for get_module_detail_from_postgres (requires DB)
"""

import pytest
from datetime import date

from etl.extractors.postgres_extractor import (
    _normalize_module_id,
    _determine_fleet_type,
    _determine_configuration,
    _ubicacion_to_coach_type,
    _ubicacion_sort_key,
)


class TestNormalizeModuleId:
    """Tests for _normalize_module_id helper."""

    def test_normalize_simple_format(self):
        """Should normalize 'M1' to 'M01'."""
        assert _normalize_module_id("M1") == "M01"
        assert _normalize_module_id("M01") == "M01"
        assert _normalize_module_id("M12") == "M12"

    def test_normalize_with_spaces(self):
        """Should handle spaces in module id."""
        assert _normalize_module_id("M 1") == "M01"
        assert _normalize_module_id("M  01") == "M01"

    def test_normalize_lowercase(self):
        """Should uppercase the prefix."""
        assert _normalize_module_id("m1") == "M01"
        assert _normalize_module_id("t5") == "T05"

    def test_normalize_with_leading_zeros(self):
        """Should handle extra leading zeros."""
        assert _normalize_module_id("M001") == "M01"
        assert _normalize_module_id("M0001") == "M01"

    def test_normalize_toshiba(self):
        """Should work for Toshiba modules."""
        assert _normalize_module_id("T1") == "T01"
        assert _normalize_module_id("T45") == "T45"

    def test_normalize_empty_or_none(self):
        """Should return empty string for None or empty input."""
        assert _normalize_module_id(None) == ""
        assert _normalize_module_id("") == ""

    def test_normalize_invalid_format(self):
        """Should return cleaned value if no pattern match."""
        assert _normalize_module_id("XYZ") == "XYZ"


class TestDetermineFleetType:
    """Tests for _determine_fleet_type helper."""

    def test_csr_from_marca(self):
        """Should detect CSR from marca_mr field."""
        assert _determine_fleet_type(None, "CSR", "M01") == "CSR"
        assert _determine_fleet_type(None, "csr", "M01") == "CSR"
        assert _determine_fleet_type(None, "CSR Zhuzhou", "M01") == "CSR"

    def test_toshiba_from_marca(self):
        """Should detect Toshiba from marca_mr field."""
        assert _determine_fleet_type(None, "TOSHIBA", "T01") == "Toshiba"
        assert _determine_fleet_type(None, "toshiba", "T01") == "Toshiba"

    def test_csr_from_module_name(self):
        """Should detect CSR from module name starting with M."""
        assert _determine_fleet_type(None, None, "M01") == "CSR"
        assert _determine_fleet_type(None, None, "M42") == "CSR"

    def test_toshiba_from_module_name(self):
        """Should detect Toshiba from module name starting with T."""
        assert _determine_fleet_type(None, None, "T01") == "Toshiba"
        assert _determine_fleet_type(None, None, "T52") == "Toshiba"

    def test_default_to_csr(self):
        """Should default to CSR when unable to determine."""
        assert _determine_fleet_type(None, None, "") == "CSR"
        assert _determine_fleet_type(None, None, "X99") == "CSR"


class TestDetermineConfiguration:
    """Tests for _determine_configuration helper."""

    def test_csr_cuadrupla(self):
        """CSR modules 1-42 are cuadruplas."""
        config, count = _determine_configuration("M01", "CSR")
        assert config == "cuadrupla"
        assert count == 4

        config, count = _determine_configuration("M42", "CSR")
        assert config == "cuadrupla"
        assert count == 4

    def test_csr_tripla(self):
        """CSR modules 43+ are triplas."""
        config, count = _determine_configuration("M43", "CSR")
        assert config == "tripla"
        assert count == 3

        config, count = _determine_configuration("M50", "CSR")
        assert config == "tripla"
        assert count == 3

    def test_toshiba_cuadrupla(self):
        """Specific Toshiba modules are cuadruplas."""
        # Known cuadruplas: 6, 11, 12, 16, 20, 24, 29, 31, 34, 39, 45, 52
        for num in [6, 11, 12, 16, 20, 24, 29, 31, 34, 39, 45, 52]:
            config, count = _determine_configuration(f"T{num:02d}", "Toshiba")
            assert config == "cuadrupla", f"T{num:02d} should be cuadrupla"
            assert count == 4

    def test_toshiba_tripla(self):
        """Other Toshiba modules are triplas."""
        for num in [1, 2, 3, 5, 7, 10, 15, 25, 30]:
            config, count = _determine_configuration(f"T{num:02d}", "Toshiba")
            assert config == "tripla", f"T{num:02d} should be tripla"
            assert count == 3


class TestUbicacionToCoachType:
    """Tests for _ubicacion_to_coach_type helper."""

    def test_csr_coach_types(self):
        """Should map CSR ubicacion codes correctly."""
        assert _ubicacion_to_coach_type("MC1") == "MC1"
        assert _ubicacion_to_coach_type("MC2") == "MC2"
        assert _ubicacion_to_coach_type("R1") == "R1"
        assert _ubicacion_to_coach_type("R2") == "R2"

    def test_toshiba_coach_types(self):
        """Should map Toshiba ubicacion codes correctly."""
        assert _ubicacion_to_coach_type("MC") == "M"
        assert _ubicacion_to_coach_type("M") == "M"
        assert _ubicacion_to_coach_type("R") == "R"
        assert _ubicacion_to_coach_type("RP") == "RP"

    def test_unknown_returns_question_mark(self):
        """Should return '?' for unknown or empty ubicacion."""
        assert _ubicacion_to_coach_type(None) == "?"
        assert _ubicacion_to_coach_type("") == "?"
        assert _ubicacion_to_coach_type("XYZ") == "?"


class TestUbicacionSortKey:
    """Tests for _ubicacion_sort_key helper."""

    def test_csr_order(self):
        """CSR coaches should sort MC1 < R1 < R2 < MC2."""
        assert _ubicacion_sort_key("MC1", "CSR") == 1
        assert _ubicacion_sort_key("R1", "CSR") == 2
        assert _ubicacion_sort_key("R2", "CSR") == 3
        assert _ubicacion_sort_key("MC2", "CSR") == 4

    def test_toshiba_order(self):
        """Toshiba coaches should sort MC/M < R < RP."""
        assert _ubicacion_sort_key("MC", "Toshiba") == 1
        assert _ubicacion_sort_key("M", "Toshiba") == 1
        assert _ubicacion_sort_key("R", "Toshiba") == 2
        assert _ubicacion_sort_key("RP", "Toshiba") == 3

    def test_unknown_last(self):
        """Unknown ubicacion should sort last (99)."""
        assert _ubicacion_sort_key(None, "CSR") == 99
        assert _ubicacion_sort_key("", "CSR") == 99
        assert _ubicacion_sort_key("XYZ", "Toshiba") == 99


# ---------------------------------------------------------------------------
# Integration tests (require database)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPostgresExtractorIntegration:
    """Integration tests for postgres_extractor functions.
    
    These tests require a Django test database with Stg* models.
    """

    def test_is_postgres_staging_available_empty(self):
        """Should return False when no staging data exists."""
        from etl.extractors.postgres_extractor import is_postgres_staging_available
        # Fresh test DB should be empty
        assert is_postgres_staging_available() is False

    def test_get_modules_from_postgres_empty(self):
        """Should return empty list when no staging data exists."""
        from etl.extractors.postgres_extractor import get_modules_from_postgres
        modules = get_modules_from_postgres()
        assert modules == []

    def test_get_module_detail_empty(self):
        """Should return empty lists when no data for module."""
        from etl.extractors.postgres_extractor import get_module_detail_from_postgres
        
        history, key_data = get_module_detail_from_postgres(
            module_db_id=999,  # Non-existent
            module_id="M99",
            fleet_type="CSR",
            km_total=100_000,
        )
        assert history == []
        # key_data should still have entries for all cycles (with None values)
        assert len(key_data) == 6  # CSR has 6 cycles

    def test_get_module_detail_with_commissioning_date(self):
        """Should use commissioning_date as fallback for DA when no data."""
        from etl.extractors.postgres_extractor import get_module_detail_from_postgres
        
        commissioning = date(2015, 5, 20)
        history, key_data = get_module_detail_from_postgres(
            module_db_id=999,
            module_id="M04",
            fleet_type="CSR",
            km_total=500_000,
            commissioning_date=commissioning,
        )
        
        # DA should have commissioning_date
        da_entry = next(k for k in key_data if k.cycle_type == "DA")
        assert da_entry.last_date == commissioning
        assert da_entry.km_at_last == 0
        assert da_entry.inherited_from == "Puesta en Servicio"
        
        # Lower cycles should inherit from DA
        for cycle in ["PE", "BA", "AN", "IB", "IQ"]:
            entry = next(k for k in key_data if k.cycle_type == cycle)
            assert entry.last_date == commissioning, f"{cycle} should inherit DA date"
            assert entry.inherited_from == "DA", f"{cycle} should show inherited_from=DA"
