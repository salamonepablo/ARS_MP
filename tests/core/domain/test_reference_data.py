"""Tests for RG reference data constants.

Verifica que los datos de referencia de RG/Puesta en Servicio
estan correctamente definidos y tienen el formato esperado.
"""
from datetime import date

import pytest

from core.domain.reference_data import RG_REFERENCE_DATES


class TestRgReferenceDates:
    """Tests para la constante RG_REFERENCE_DATES."""

    def test_constant_exists_and_is_dict(self):
        """La constante debe existir y ser un diccionario."""
        assert isinstance(RG_REFERENCE_DATES, dict)

    def test_total_entry_count(self):
        """Debe tener 110 entradas totales (85 CSR + 25 Toshiba)."""
        assert len(RG_REFERENCE_DATES) == 110

    def test_csr_module_count(self):
        """Debe tener 85 modulos CSR (M01-M86, sin M67)."""
        csr_modules = [k for k in RG_REFERENCE_DATES if k.startswith("M")]
        assert len(csr_modules) == 85

    def test_toshiba_module_count(self):
        """Debe tener 25 modulos Toshiba."""
        toshiba_modules = [k for k in RG_REFERENCE_DATES if k.startswith("T")]
        assert len(toshiba_modules) == 25

    def test_m67_not_in_data(self):
        """M67 no debe estar (nunca fue puesto en servicio, donante de repuestos)."""
        assert "M67" not in RG_REFERENCE_DATES

    def test_m47_is_included(self):
        """M47 debe estar incluido (fuera de servicio pero fue puesto en servicio)."""
        assert "M47" in RG_REFERENCE_DATES
        assert RG_REFERENCE_DATES["M47"] == (date(2016, 1, 31), "Puesta en Servicio")

    def test_key_format(self):
        """Las claves deben tener formato M## o T## (2 digitos)."""
        import re
        pattern = re.compile(r"^[MT]\d{2}$")
        for key in RG_REFERENCE_DATES:
            assert pattern.match(key), f"Invalid key format: {key}"

    def test_value_format(self):
        """Los valores deben ser tuplas (date, str)."""
        for key, value in RG_REFERENCE_DATES.items():
            assert isinstance(value, tuple), f"Value for {key} is not a tuple"
            assert len(value) == 2, f"Value for {key} should have 2 elements"
            assert isinstance(value[0], date), f"First element of {key} should be date"
            assert isinstance(value[1], str), f"Second element of {key} should be str"

    def test_csr_reference_type(self):
        """Todos los modulos CSR deben tener tipo 'Puesta en Servicio'."""
        for key, (_, ref_type) in RG_REFERENCE_DATES.items():
            if key.startswith("M"):
                assert ref_type == "Puesta en Servicio", f"{key} has wrong ref type: {ref_type}"

    def test_toshiba_reference_type(self):
        """Todos los modulos Toshiba deben tener tipo 'RG'."""
        for key, (_, ref_type) in RG_REFERENCE_DATES.items():
            if key.startswith("T"):
                assert ref_type == "RG", f"{key} has wrong ref type: {ref_type}"

    def test_sample_csr_entries(self):
        """Verifica algunas entradas CSR especificas."""
        # M01 - fecha actualizada
        assert RG_REFERENCE_DATES["M01"] == (date(2017, 9, 30), "Puesta en Servicio")
        # M02
        assert RG_REFERENCE_DATES["M02"] == (date(2015, 8, 31), "Puesta en Servicio")
        # M35 - fecha mas reciente (2019)
        assert RG_REFERENCE_DATES["M35"] == (date(2019, 12, 28), "Puesta en Servicio")
        # M86 - ultimo modulo CSR
        assert RG_REFERENCE_DATES["M86"] == (date(2017, 6, 30), "Puesta en Servicio")

    def test_sample_toshiba_entries(self):
        """Verifica algunas entradas Toshiba especificas."""
        # T04
        assert RG_REFERENCE_DATES["T04"] == (date(2023, 12, 15), "RG")
        # T12 - fecha mas antigua (2011)
        assert RG_REFERENCE_DATES["T12"] == (date(2011, 6, 28), "RG")
        # T52 - ultimo en la lista
        assert RG_REFERENCE_DATES["T52"] == (date(2024, 8, 30), "RG")

    def test_dates_are_reasonable(self):
        """Las fechas deben estar en rangos razonables (2011-2025)."""
        min_date = date(2011, 1, 1)
        max_date = date(2026, 1, 1)
        for key, (ref_date, _) in RG_REFERENCE_DATES.items():
            assert min_date <= ref_date <= max_date, f"{key} has unreasonable date: {ref_date}"
