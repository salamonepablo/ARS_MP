"""
Tests for maintenance projection and history services.

Tests cover:
- MaintenanceProjectionService: next intervention calculation
- MaintenanceHistoryService: key data extraction and history filtering
- Edge cases: no data, single cycle, overdue cycles
"""

import pytest
from datetime import date, timedelta

from core.services.maintenance_projection import (
    AVG_DAILY_KM,
    CSR_MAINTENANCE_CYCLES,
    TOSHIBA_MAINTENANCE_CYCLES,
    TASK_TO_CYCLE,
    MaintenanceHistoryService,
    MaintenanceProjectionService,
    ProjectionResult,
)


class TestMaintenanceProjectionService:
    """Tests for MaintenanceProjectionService."""

    def test_get_cycles_for_csr(self):
        """Should return CSR maintenance cycles."""
        cycles = MaintenanceProjectionService.get_cycles_for_fleet("CSR")
        assert cycles == CSR_MAINTENANCE_CYCLES
        assert len(cycles) == 4
        assert cycles[0][0] == "AN"
        assert cycles[-1][0] == "DA"

    def test_get_cycles_for_toshiba(self):
        """Should return Toshiba maintenance cycles."""
        cycles = MaintenanceProjectionService.get_cycles_for_fleet("Toshiba")
        assert cycles == TOSHIBA_MAINTENANCE_CYCLES
        assert len(cycles) == 2
        assert cycles[0][0] == "RB"
        assert cycles[1][0] == "RG"

    def test_project_returns_none_with_no_data(self):
        """Should return None when key_data is empty."""
        result = MaintenanceProjectionService.project_next_intervention(
            fleet_type="CSR",
            km_total=500_000,
            key_data=[],
        )
        assert result is None

    def test_project_csr_picks_soonest_cycle(self):
        """Should pick the cycle with smallest km_remaining."""
        key_data = [
            {"cycle_type": "AN", "cycle_km": 187_500, "km_at_last": 400_000, "last_date": date(2025, 6, 1)},
            {"cycle_type": "BA", "cycle_km": 375_000, "km_at_last": 200_000, "last_date": date(2024, 1, 1)},
        ]
        result = MaintenanceProjectionService.project_next_intervention(
            fleet_type="CSR",
            km_total=500_000,
            key_data=key_data,
            reference_date=date(2026, 1, 1),
        )
        assert result is not None
        # AN: km_since = 500k - 400k = 100k, remaining = 187.5k - 100k = 87.5k
        # BA: km_since = 500k - 200k = 300k, remaining = 375k - 300k = 75k
        assert result.cycle_type == "BA"
        assert result.km_remaining == 75_000

    def test_project_toshiba_with_rg_data(self):
        """Should project Toshiba RG/RB correctly."""
        key_data = [
            {"cycle_type": "RB", "cycle_km": 300_000, "km_at_last": 350_000, "last_date": date(2025, 3, 1)},
            {"cycle_type": "RG", "cycle_km": 600_000, "km_at_last": 100_000, "last_date": date(2023, 1, 1)},
        ]
        result = MaintenanceProjectionService.project_next_intervention(
            fleet_type="Toshiba",
            km_total=550_000,
            key_data=key_data,
            reference_date=date(2026, 1, 1),
        )
        assert result is not None
        # RB: km_since = 550k - 350k = 200k, remaining = 300k - 200k = 100k
        # RG: km_since = 550k - 100k = 450k, remaining = 600k - 450k = 150k
        assert result.cycle_type == "RB"
        assert result.km_remaining == 100_000

    def test_project_overdue_cycle(self):
        """When a cycle is overdue, km_remaining should be 0."""
        key_data = [
            {"cycle_type": "AN", "cycle_km": 187_500, "km_at_last": 100_000, "last_date": date(2024, 1, 1)},
        ]
        result = MaintenanceProjectionService.project_next_intervention(
            fleet_type="CSR",
            km_total=400_000,
            key_data=key_data,
            reference_date=date(2026, 1, 1),
        )
        assert result is not None
        # km_since = 400k - 100k = 300k > 187.5k => overdue
        assert result.km_remaining == 0
        # Estimated date should be the reference date (already overdue)
        assert result.estimated_date == date(2026, 1, 1)

    def test_project_no_previous_intervention(self):
        """When km_at_last is None, should count from zero km."""
        key_data = [
            {"cycle_type": "RG", "cycle_km": 600_000, "km_at_last": None, "last_date": None},
        ]
        result = MaintenanceProjectionService.project_next_intervention(
            fleet_type="Toshiba",
            km_total=200_000,
            key_data=key_data,
            reference_date=date(2026, 1, 1),
        )
        assert result is not None
        # km_since = 200_000 (from 0), remaining = 600k - 200k = 400k
        assert result.km_remaining == 400_000
        assert result.km_since_last == 200_000

    def test_project_estimated_date_calculation(self):
        """Estimated date should be ref_date + km_remaining / daily_km."""
        key_data = [
            {"cycle_type": "AN", "cycle_km": 187_500, "km_at_last": 400_000, "last_date": date(2025, 6, 1)},
        ]
        result = MaintenanceProjectionService.project_next_intervention(
            fleet_type="CSR",
            km_total=500_000,
            key_data=key_data,
            avg_daily_km=392,
            reference_date=date(2026, 1, 1),
        )
        assert result is not None
        # km_remaining = 187_500 - 100_000 = 87_500
        # days = ceil(87_500 / 392) = 224
        expected_date = date(2026, 1, 1) + timedelta(days=224)
        assert result.estimated_date == expected_date

    def test_project_uses_fleet_default_daily_km(self):
        """Should use fleet-specific avg_daily_km when not overridden."""
        key_data = [
            {"cycle_type": "RB", "cycle_km": 300_000, "km_at_last": 200_000, "last_date": date(2025, 6, 1)},
        ]
        result = MaintenanceProjectionService.project_next_intervention(
            fleet_type="Toshiba",
            km_total=250_000,
            key_data=key_data,
            reference_date=date(2026, 1, 1),
        )
        assert result is not None
        # km_remaining = 300k - 50k = 250k
        import math
        expected_days = math.ceil(250_000 / 260)
        expected_date = date(2026, 1, 1) + timedelta(days=expected_days)
        assert result.estimated_date == expected_date


class TestMaintenanceHistoryService:
    """Tests for MaintenanceHistoryService."""

    def test_get_last_intervention_per_cycle_csr(self):
        """Should return one entry per CSR cycle type."""
        history = [
            {"task_type": "AN1", "event_date": date(2025, 6, 1), "km_at_event": 300_000},
            {"task_type": "AN3", "event_date": date(2025, 8, 1), "km_at_event": 320_000},
            {"task_type": "BA1", "event_date": date(2025, 1, 1), "km_at_event": 250_000},
            {"task_type": "IQ", "event_date": date(2025, 9, 1), "km_at_event": 340_000},
        ]
        result = MaintenanceHistoryService.get_last_intervention_per_cycle(
            fleet_type="CSR",
            history=history,
            km_total=400_000,
        )
        # Should have 4 entries (AN, BA, PE, DA)
        assert len(result) == 4
        
        an_entry = next(r for r in result if r["cycle_type"] == "AN")
        assert an_entry["last_date"] == date(2025, 8, 1)  # AN3 is newer
        assert an_entry["km_at_last"] == 320_000
        assert an_entry["km_since"] == 80_000

        ba_entry = next(r for r in result if r["cycle_type"] == "BA")
        assert ba_entry["last_date"] == date(2025, 1, 1)
        assert ba_entry["km_since"] == 150_000

        pe_entry = next(r for r in result if r["cycle_type"] == "PE")
        assert pe_entry["last_date"] is None
        assert pe_entry["km_since"] is None

    def test_get_last_intervention_per_cycle_toshiba(self):
        """Should return one entry per Toshiba cycle type."""
        history = [
            {"task_type": "RB", "event_date": date(2025, 3, 1), "km_at_event": 400_000},
            {"task_type": "RG", "event_date": date(2024, 1, 1), "km_at_event": 200_000},
        ]
        result = MaintenanceHistoryService.get_last_intervention_per_cycle(
            fleet_type="Toshiba",
            history=history,
            km_total=550_000,
        )
        assert len(result) == 2

        rb_entry = next(r for r in result if r["cycle_type"] == "RB")
        assert rb_entry["km_since"] == 150_000

        rg_entry = next(r for r in result if r["cycle_type"] == "RG")
        assert rg_entry["km_since"] == 350_000

    def test_get_last_intervention_empty_history(self):
        """Should return entries with None values when no history."""
        result = MaintenanceHistoryService.get_last_intervention_per_cycle(
            fleet_type="CSR",
            history=[],
            km_total=500_000,
        )
        assert len(result) == 4
        for entry in result:
            assert entry["last_date"] is None
            assert entry["km_at_last"] is None
            assert entry["km_since"] is None

    def test_filter_history_last_year(self):
        """Should only return events within 365 days of reference date."""
        history = [
            {"event_date": date(2025, 6, 1), "task_type": "IQ"},
            {"event_date": date(2025, 1, 1), "task_type": "IB"},
            {"event_date": date(2024, 1, 1), "task_type": "AN1"},  # > 365 days
            {"event_date": date(2023, 6, 1), "task_type": "BA1"},  # > 365 days
        ]
        result = MaintenanceHistoryService.filter_history_last_year(
            history,
            reference_date=date(2025, 12, 1),
        )
        assert len(result) == 2
        assert result[0]["event_date"] == date(2025, 6, 1)
        assert result[1]["event_date"] == date(2025, 1, 1)

    def test_filter_history_sorted_descending(self):
        """Result should be sorted by date descending."""
        history = [
            {"event_date": date(2025, 3, 1), "task_type": "IQ"},
            {"event_date": date(2025, 9, 1), "task_type": "IB"},
            {"event_date": date(2025, 6, 1), "task_type": "AN1"},
        ]
        result = MaintenanceHistoryService.filter_history_last_year(
            history,
            reference_date=date(2026, 1, 1),
        )
        dates = [e["event_date"] for e in result]
        assert dates == sorted(dates, reverse=True)

    def test_filter_history_empty(self):
        """Should handle empty history gracefully."""
        result = MaintenanceHistoryService.filter_history_last_year([])
        assert result == []


class TestTaskToCycleMapping:
    """Tests for the TASK_TO_CYCLE mapping."""

    def test_an_variants_map_to_an(self):
        """All AN subtypes should map to AN cycle."""
        for task in ["AN1", "AN2", "AN3", "AN4", "AN5", "AN6", "AN"]:
            assert TASK_TO_CYCLE[task] == "AN"

    def test_ba_variants_map_to_ba(self):
        """All BA subtypes should map to BA cycle."""
        for task in ["BA1", "BA2", "BA3", "BA"]:
            assert TASK_TO_CYCLE[task] == "BA"

    def test_rs_maps_to_pe(self):
        """RS (Reparación Pentanual) should map to PE cycle."""
        assert TASK_TO_CYCLE["RS"] == "PE"

    def test_da_and_rg_mappings(self):
        """DA maps to DA, RG maps to RG."""
        assert TASK_TO_CYCLE["DA"] == "DA"
        assert TASK_TO_CYCLE["RG"] == "RG"

    def test_toshiba_tasks(self):
        """Toshiba-specific tasks should be mapped."""
        assert TASK_TO_CYCLE["RB"] == "RB"
        assert TASK_TO_CYCLE["MEN"] == "MEN"

    def test_iq_variants(self):
        """IQ subtypes should map to IQ."""
        for task in ["IQ", "IQ1", "IQ2", "IQ3"]:
            assert TASK_TO_CYCLE[task] == "IQ"
