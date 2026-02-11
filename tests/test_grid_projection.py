"""
Tests for grid projection service (RED phase).

Tests cover:
- Monthly km projection for a single module/cycle
- Prorated current month calculation (remaining days)
- Threshold detection (exceeded flag)
- Multi-cycle projection for a module
- Full grid generation for fleet
"""

import pytest
from datetime import date

from core.services.grid_projection import (
    DEFAULT_MONTHS,
    DEFAULT_AVG_MONTHLY_KM,
    CYCLE_COLORS,
    MonthProjection,
    CycleRow,
    ModuleGridData,
    GridProjectionService,
)


class TestConstants:
    """Verify default constants are correctly defined."""

    def test_default_months(self):
        assert DEFAULT_MONTHS == 18

    def test_default_avg_monthly_km(self):
        assert DEFAULT_AVG_MONTHLY_KM["CSR"] == 12_000
        assert DEFAULT_AVG_MONTHLY_KM["Toshiba"] == 8_000

    def test_cycle_colors_csr(self):
        assert "AN" in CYCLE_COLORS
        assert "BA" in CYCLE_COLORS
        assert "PE" in CYCLE_COLORS
        assert "DA" in CYCLE_COLORS
        # Each color has bg and text keys
        for cycle in ("AN", "BA", "PE", "DA"):
            assert "bg" in CYCLE_COLORS[cycle]
            assert "text" in CYCLE_COLORS[cycle]

    def test_cycle_colors_toshiba(self):
        assert "RB" in CYCLE_COLORS
        assert "RG" in CYCLE_COLORS


class TestProjectSingleCycle:
    """Test projection of a single cycle for a single module."""

    def test_basic_projection_18_months(self):
        """Should project km accumulation for 18 months."""
        result = GridProjectionService.project_cycle(
            km_since=50_000,
            cycle_km=187_500,
            avg_monthly_km=12_000,
            months=18,
            reference_date=date(2026, 2, 1),  # Start of month for simplicity
        )
        assert len(result) == 18
        # First month: full 12k since reference is start of month
        # km_since starts at 50k, so first month ~50k + prorated
        assert all(isinstance(m, MonthProjection) for m in result)

    def test_prorated_current_month(self):
        """Current month should only add km for remaining days."""
        # Feb 11, 2026 -> 17 days remaining in Feb (28 days)
        result = GridProjectionService.project_cycle(
            km_since=100_000,
            cycle_km=187_500,
            avg_monthly_km=12_000,
            months=3,
            reference_date=date(2026, 2, 11),
        )
        first = result[0]
        # Prorated: 12000 / 28 * 17 ≈ 7286 (approx)
        # So km_accumulated ≈ 100_000 + 7_286 = 107_286
        assert first.km_accumulated > 100_000
        assert first.km_accumulated < 100_000 + 12_000  # Less than full month

    def test_second_month_adds_full_km(self):
        """Second and subsequent months should add full avg_monthly_km."""
        result = GridProjectionService.project_cycle(
            km_since=100_000,
            cycle_km=187_500,
            avg_monthly_km=12_000,
            months=3,
            reference_date=date(2026, 2, 1),
        )
        # Difference between month 2 and month 1 should be 12_000
        diff = result[1].km_accumulated - result[0].km_accumulated
        assert diff == 12_000

    def test_exceeded_flag_set_when_threshold_reached(self):
        """exceeded should be True when km_accumulated >= cycle_km."""
        result = GridProjectionService.project_cycle(
            km_since=180_000,  # Close to 187_500
            cycle_km=187_500,
            avg_monthly_km=12_000,
            months=3,
            reference_date=date(2026, 2, 1),
        )
        # Month 1: 180k + 12k = 192k > 187.5k -> exceeded
        assert result[0].exceeded is True

    def test_not_exceeded_when_within_threshold(self):
        """exceeded should be False when km_accumulated < cycle_km."""
        result = GridProjectionService.project_cycle(
            km_since=10_000,
            cycle_km=187_500,
            avg_monthly_km=12_000,
            months=2,
            reference_date=date(2026, 2, 1),
        )
        # Month 1: 10k + 12k = 22k < 187.5k
        assert result[0].exceeded is False

    def test_month_labels_format(self):
        """Each MonthProjection should have correct month_label."""
        result = GridProjectionService.project_cycle(
            km_since=0,
            cycle_km=187_500,
            avg_monthly_km=12_000,
            months=3,
            reference_date=date(2026, 2, 15),
        )
        assert result[0].month_label == "Feb-26"
        assert result[1].month_label == "Mar-26"
        assert result[2].month_label == "Apr-26"

    def test_zero_km_since(self):
        """Should work when starting from 0 km (fresh after intervention)."""
        result = GridProjectionService.project_cycle(
            km_since=0,
            cycle_km=187_500,
            avg_monthly_km=12_000,
            months=2,
            reference_date=date(2026, 2, 1),
        )
        assert result[0].km_accumulated == 12_000
        assert result[0].exceeded is False

    def test_none_km_since_treated_as_zero(self):
        """When km_since is None, treat as 0 (no data available)."""
        result = GridProjectionService.project_cycle(
            km_since=None,
            cycle_km=187_500,
            avg_monthly_km=12_000,
            months=2,
            reference_date=date(2026, 2, 1),
        )
        assert result[0].km_accumulated == 12_000


class TestProjectModule:
    """Test projection of all heavy cycles for a single module."""

    def test_csr_module_returns_4_cycle_rows(self):
        """CSR module should have 4 heavy cycle rows (AN, BA, PE, DA)."""
        key_data = [
            {"cycle_type": "AN", "cycle_km": 187_500, "km_since": 50_000},
            {"cycle_type": "BA", "cycle_km": 375_000, "km_since": 100_000},
            {"cycle_type": "PE", "cycle_km": 750_000, "km_since": 200_000},
            {"cycle_type": "DA", "cycle_km": 1_500_000, "km_since": 300_000},
        ]
        result = GridProjectionService.project_module(
            module_id="M01",
            fleet_type="CSR",
            key_data=key_data,
            avg_monthly_km=12_000,
            months=18,
            reference_date=date(2026, 2, 1),
        )
        assert isinstance(result, ModuleGridData)
        assert result.module_id == "M01"
        assert len(result.cycle_rows) == 4
        assert result.cycle_rows[0].cycle_type == "AN"
        assert result.cycle_rows[-1].cycle_type == "DA"

    def test_toshiba_module_returns_2_cycle_rows(self):
        """Toshiba module should have 2 heavy cycle rows (RB, RG)."""
        key_data = [
            {"cycle_type": "RB", "cycle_km": 300_000, "km_since": 50_000},
            {"cycle_type": "RG", "cycle_km": 600_000, "km_since": 100_000},
        ]
        result = GridProjectionService.project_module(
            module_id="T01",
            fleet_type="Toshiba",
            key_data=key_data,
            avg_monthly_km=8_000,
            months=18,
            reference_date=date(2026, 2, 1),
        )
        assert len(result.cycle_rows) == 2
        assert result.cycle_rows[0].cycle_type == "RB"
        assert result.cycle_rows[1].cycle_type == "RG"


class TestGenerateGrid:
    """Test full grid generation for a fleet."""

    def test_grid_returns_list_of_module_grid_data(self):
        """Should return one ModuleGridData per module."""
        modules_data = [
            {
                "module_id": "M01",
                "fleet_type": "CSR",
                "key_data": [
                    {"cycle_type": "AN", "cycle_km": 187_500, "km_since": 50_000},
                    {"cycle_type": "BA", "cycle_km": 375_000, "km_since": 100_000},
                    {"cycle_type": "PE", "cycle_km": 750_000, "km_since": 200_000},
                    {"cycle_type": "DA", "cycle_km": 1_500_000, "km_since": 300_000},
                ],
            },
            {
                "module_id": "M02",
                "fleet_type": "CSR",
                "key_data": [
                    {"cycle_type": "AN", "cycle_km": 187_500, "km_since": 10_000},
                    {"cycle_type": "BA", "cycle_km": 375_000, "km_since": 20_000},
                    {"cycle_type": "PE", "cycle_km": 750_000, "km_since": 40_000},
                    {"cycle_type": "DA", "cycle_km": 1_500_000, "km_since": 80_000},
                ],
            },
        ]
        result = GridProjectionService.generate_grid(
            modules_data=modules_data,
            avg_monthly_km=12_000,
            months=6,
            reference_date=date(2026, 2, 1),
        )
        assert len(result) == 2
        assert result[0].module_id == "M01"
        assert result[1].module_id == "M02"

    def test_grid_month_headers(self):
        """Should return correct month headers."""
        headers = GridProjectionService.get_month_headers(
            months=3,
            reference_date=date(2026, 2, 15),
        )
        assert headers == ["Feb-26", "Mar-26", "Apr-26"]

    def test_grid_empty_input(self):
        """Should handle empty module list."""
        result = GridProjectionService.generate_grid(
            modules_data=[],
            avg_monthly_km=12_000,
            months=6,
            reference_date=date(2026, 2, 1),
        )
        assert result == []
