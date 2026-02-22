"""
Tests for fleet stub_data module.

Tests cover:
- ModuleData dataclass and computed properties
- CSR module generation rules (85 modules, M67 excluded, cuadrupla/tripla split)
- Toshiba module generation rules (25 modules with real IDs from reference_data)
- Fleet summary calculations
"""

from datetime import date, timedelta
from web.fleet.stub_data import (
    ModuleData,
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
    """Tests for CSR module generation rules.
    
    Nota de negocio: M67 está excluido porque nunca fue puesto en servicio
    y se usa como donante de partes para la flota activa.
    """

    def test_generates_85_csr_modules(self, csr_modules):
        """Genera exactamente 85 módulos CSR (M67 excluido)."""
        assert len(csr_modules) == 85

    def test_m67_excluded(self, csr_modules):
        """M67 no debe existir - nunca fue puesto en servicio."""
        module_ids = [m.module_id for m in csr_modules]
        assert "M67" not in module_ids

    def test_all_modules_are_csr_type(self, csr_modules):
        """All modules should have fleet_type='CSR'."""
        for module in csr_modules:
            assert module.fleet_type == "CSR"

    def test_module_ids_format(self, csr_modules):
        """Module IDs should be M01-M86 format (excluding M67)."""
        expected_ids = [f"M{i:02d}" for i in range(1, 87) if i != 67]
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
        """Modules M43-M86 should be triplas with 3 coaches (M67 excluido)."""
        triplas = [m for m in csr_modules if m.module_number > 42]
        
        # 44 triplas originalmente, menos M67 = 43
        assert len(triplas) == 43
        for module in triplas:
            assert module.configuration == "tripla"
            assert module.coach_count == 3

    def test_csr_maintenance_types(self, csr_modules):
        """CSR modules should only have valid CSR maintenance types."""
        valid_types = {"IQ", "IB", "AN", "BA", "RS", "DA"}
        for module in csr_modules:
            assert module.last_maintenance_type in valid_types

    def test_csr_modules_have_coaches(self, csr_modules):
        """Todos los módulos CSR deben tener composición de coches."""
        for module in csr_modules:
            assert len(module.coaches) > 0
            assert module.coach_composition_str != ""

    def test_csr_modules_have_reference_date(self, csr_modules):
        """Todos los módulos CSR deben tener fecha de puesta en servicio."""
        for module in csr_modules:
            assert module.reference_date is not None
            assert module.reference_type == "Puesta en Servicio"


class TestToshibaModuleGeneration:
    """Tests for Toshiba module generation rules.
    
    Nota de negocio: Los IDs de Toshiba vienen de reference_data.py y no son
    secuenciales (T04, T06, T09, etc.) porque reflejan la numeración real
    de la flota Toshiba.
    """

    def test_generates_25_toshiba_modules(self, toshiba_modules):
        """Should generate exactly 25 Toshiba modules."""
        assert len(toshiba_modules) == 25

    def test_all_modules_are_toshiba_type(self, toshiba_modules):
        """All modules should have fleet_type='Toshiba'."""
        for module in toshiba_modules:
            assert module.fleet_type == "Toshiba"

    def test_module_ids_from_reference_data(self, toshiba_modules):
        """Module IDs deben coincidir con reference_data (no secuenciales)."""
        from core.domain.reference_data import RG_REFERENCE_DATES
        expected_ids = sorted(
            [mid for mid in RG_REFERENCE_DATES.keys() if mid.startswith("T")],
            key=lambda x: int(x[1:])
        )
        actual_ids = [m.module_id for m in toshiba_modules]
        assert actual_ids == expected_ids

    def test_12_cuadruplas_and_13_triplas(self, toshiba_modules):
        """Toshiba: 12 cuadruplas y 13 triplas."""
        cuadruplas = [m for m in toshiba_modules if m.configuration == "cuadrupla"]
        triplas = [m for m in toshiba_modules if m.configuration == "tripla"]
        
        assert len(cuadruplas) == 12
        assert len(triplas) == 13
        
        for module in cuadruplas:
            assert module.coach_count == 4
        for module in triplas:
            assert module.coach_count == 3

    def test_toshiba_maintenance_types(self, toshiba_modules):
        """Toshiba modules should only have valid Toshiba maintenance types."""
        valid_types = {"MEN", "RB", "RG"}
        for module in toshiba_modules:
            assert module.last_maintenance_type in valid_types

    def test_toshiba_modules_have_coaches(self, toshiba_modules):
        """Todos los módulos Toshiba deben tener composición de coches."""
        for module in toshiba_modules:
            assert len(module.coaches) > 0
            assert module.coach_composition_str != ""

    def test_toshiba_modules_have_rg_date(self, toshiba_modules):
        """Todos los módulos Toshiba deben tener fecha de RG."""
        for module in toshiba_modules:
            assert module.reference_date is not None
            assert module.reference_type == "RG"
            assert module.last_rg_date is not None


class TestGetAllModules:
    """Tests for combined module retrieval."""

    def test_returns_110_total_modules(self, all_modules):
        """Retorna 85 CSR + 25 Toshiba = 110 módulos (M67 excluido)."""
        assert len(all_modules) == 110

    def test_contains_85_csr_and_25_toshiba(self, all_modules):
        """Contiene exactamente 85 CSR y 25 Toshiba."""
        csr = [m for m in all_modules if m.fleet_type == "CSR"]
        toshiba = [m for m in all_modules if m.fleet_type == "Toshiba"]
        
        assert len(csr) == 85
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
        """Summary should have correct module counts (M67 excluido)."""
        summary = get_fleet_summary(all_modules)
        
        assert summary["csr_count"] == 85
        assert summary["toshiba_count"] == 25
        assert summary["total_count"] == 110

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
