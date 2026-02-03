"""
Tests for fleet stub_data module.

Tests cover:
- ModuleData dataclass and computed properties
- CSR module generation rules (86 modules, cuadrupla/tripla split)
- Toshiba module generation rules (25 modules, cuadrupla/tripla split)
- Fleet summary calculations
"""

import pytest
from datetime import date, timedelta
from web.fleet.stub_data import (
    ModuleData,
    generate_csr_modules,
    generate_toshiba_modules,
    get_all_modules,
    get_fleet_summary,
)


class TestModuleData:
    """Tests for ModuleData dataclass."""

    def test_module_data_creation(self, sample_module_data):
        """ModuleData should be created with all required fields."""
        assert sample_module_data.module_id == "M01"
        assert sample_module_data.module_number == 1
        assert sample_module_data.fleet_type == "CSR"
        assert sample_module_data.configuration == "cuadrupla"
        assert sample_module_data.coach_count == 4

    def test_km_since_maintenance_calculation(self, sample_module_data):
        """km_since_maintenance should be total - at_maintenance."""
        # 500000 - 450000 = 50000
        assert sample_module_data.km_since_maintenance == 50000

    def test_days_since_maintenance_calculation(self):
        """days_since_maintenance should calculate correctly from date."""
        today = date.today()
        ten_days_ago = today - timedelta(days=10)

        module = ModuleData(
            module_id="M01",
            module_number=1,
            fleet_type="CSR",
            configuration="cuadrupla",
            coach_count=4,
            km_current_month=10000,
            km_total_accumulated=500000,
            last_maintenance_date=ten_days_ago,
            last_maintenance_type="IQ",
            km_at_last_maintenance=450000,
        )

        assert module.days_since_maintenance == 10


class TestCSRModuleGeneration:
    """Tests for CSR module generation rules."""

    def test_generates_86_csr_modules(self, csr_modules):
        """Should generate exactly 86 CSR modules."""
        assert len(csr_modules) == 86

    def test_all_modules_are_csr_type(self, csr_modules):
        """All modules should have fleet_type='CSR'."""
        for module in csr_modules:
            assert module.fleet_type == "CSR"

    def test_module_ids_format(self, csr_modules):
        """Module IDs should be M01-M86 format."""
        expected_ids = [f"M{i:02d}" for i in range(1, 87)]
        actual_ids = [m.module_id for m in csr_modules]
        assert actual_ids == expected_ids

    def test_modules_1_to_42_are_cuadruplas(self, csr_modules):
        """Modules M01-M42 should be cuadruplas with 4 coaches."""
        cuadruplas = [m for m in csr_modules if m.module_number <= 42]
        
        assert len(cuadruplas) == 42
        for module in cuadruplas:
            assert module.configuration == "cuadrupla"
            assert module.coach_count == 4

    def test_modules_43_to_86_are_triplas(self, csr_modules):
        """Modules M43-M86 should be triplas with 3 coaches."""
        triplas = [m for m in csr_modules if m.module_number > 42]
        
        assert len(triplas) == 44
        for module in triplas:
            assert module.configuration == "tripla"
            assert module.coach_count == 3

    def test_csr_maintenance_types(self, csr_modules):
        """CSR modules should only have valid CSR maintenance types."""
        valid_types = {"IQ", "IB", "AN", "BA", "RS", "DA"}
        for module in csr_modules:
            assert module.last_maintenance_type in valid_types


class TestToshibaModuleGeneration:
    """Tests for Toshiba module generation rules."""

    def test_generates_25_toshiba_modules(self, toshiba_modules):
        """Should generate exactly 25 Toshiba modules."""
        assert len(toshiba_modules) == 25

    def test_all_modules_are_toshiba_type(self, toshiba_modules):
        """All modules should have fleet_type='Toshiba'."""
        for module in toshiba_modules:
            assert module.fleet_type == "Toshiba"

    def test_module_ids_format(self, toshiba_modules):
        """Module IDs should be T01-T25 format."""
        expected_ids = [f"T{i:02d}" for i in range(1, 26)]
        actual_ids = [m.module_id for m in toshiba_modules]
        assert actual_ids == expected_ids

    def test_modules_1_to_12_are_cuadruplas(self, toshiba_modules):
        """Modules T01-T12 should be cuadruplas with 4 coaches."""
        cuadruplas = [m for m in toshiba_modules if m.module_number <= 12]
        
        assert len(cuadruplas) == 12
        for module in cuadruplas:
            assert module.configuration == "cuadrupla"
            assert module.coach_count == 4

    def test_modules_13_to_25_are_triplas(self, toshiba_modules):
        """Modules T13-T25 should be triplas with 3 coaches."""
        triplas = [m for m in toshiba_modules if m.module_number > 12]
        
        assert len(triplas) == 13
        for module in triplas:
            assert module.configuration == "tripla"
            assert module.coach_count == 3

    def test_toshiba_maintenance_types(self, toshiba_modules):
        """Toshiba modules should only have valid Toshiba maintenance types."""
        valid_types = {"MEN", "RB", "RG"}
        for module in toshiba_modules:
            assert module.last_maintenance_type in valid_types


class TestGetAllModules:
    """Tests for combined module retrieval."""

    def test_returns_111_total_modules(self, all_modules):
        """Should return 86 CSR + 25 Toshiba = 111 modules."""
        assert len(all_modules) == 111

    def test_contains_86_csr_and_25_toshiba(self, all_modules):
        """Should contain exactly 86 CSR and 25 Toshiba."""
        csr = [m for m in all_modules if m.fleet_type == "CSR"]
        toshiba = [m for m in all_modules if m.fleet_type == "Toshiba"]
        
        assert len(csr) == 86
        assert len(toshiba) == 25

    def test_consistent_with_seed(self):
        """Multiple calls should return same data (seeded)."""
        modules1 = get_all_modules()
        modules2 = get_all_modules()
        
        # Check first module is identical
        assert modules1[0].km_current_month == modules2[0].km_current_month
        assert modules1[0].km_total_accumulated == modules2[0].km_total_accumulated


class TestFleetSummary:
    """Tests for fleet summary KPI calculations."""

    def test_summary_counts(self, all_modules):
        """Summary should have correct module counts."""
        summary = get_fleet_summary(all_modules)
        
        assert summary["csr_count"] == 86
        assert summary["toshiba_count"] == 25
        assert summary["total_count"] == 111

    def test_summary_km_month_totals(self, all_modules):
        """km_month totals should be sum of individual modules."""
        summary = get_fleet_summary(all_modules)
        
        csr_km = sum(m.km_current_month for m in all_modules if m.fleet_type == "CSR")
        toshiba_km = sum(m.km_current_month for m in all_modules if m.fleet_type == "Toshiba")
        
        assert summary["csr_km_month"] == csr_km
        assert summary["toshiba_km_month"] == toshiba_km
        assert summary["total_km_month"] == csr_km + toshiba_km

    def test_summary_km_total_accumulated(self, all_modules):
        """km_total should be sum of accumulated km."""
        summary = get_fleet_summary(all_modules)
        
        total_accumulated = sum(m.km_total_accumulated for m in all_modules)
        assert summary["total_km_total"] == total_accumulated

    def test_summary_with_empty_list(self):
        """Summary should handle empty list gracefully."""
        summary = get_fleet_summary([])
        
        assert summary["csr_count"] == 0
        assert summary["toshiba_count"] == 0
        assert summary["total_count"] == 0
        assert summary["total_km_month"] == 0
