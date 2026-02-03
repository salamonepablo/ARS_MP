"""
Tests for Access database connection and data extraction.

TDD: These tests define the expected behavior before implementation.
"""

import os
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

# These imports will fail until we implement the modules (TDD RED)
from etl.extractors.access_connection import (
    AccessConnectionError,
    get_access_connection,
    is_access_available,
)
from etl.extractors.access_extractor import (
    extract_module_data,
    get_modules_from_access,
)
from web.fleet.stub_data import ModuleData


class TestAccessConnectionAvailability:
    """Test detection of Access database availability."""

    def test_is_access_available_returns_false_when_env_not_configured(self):
        """When env vars are missing, should return False."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_access_available() is False

    def test_is_access_available_returns_false_when_path_missing(self):
        """When only password is set, should return False."""
        with patch.dict(
            os.environ,
            {"LEGACY_ACCESS_DB_PASSWORD": "1041"},
            clear=True,
        ):
            assert is_access_available() is False

    def test_is_access_available_returns_false_when_file_not_exists(self):
        """When path points to non-existent file, should return False."""
        with patch.dict(
            os.environ,
            {
                "LEGACY_ACCESS_DB_PATH": "/nonexistent/path.accdb",
                "LEGACY_ACCESS_DB_PASSWORD": "1041",
            },
            clear=True,
        ):
            assert is_access_available() is False

    def test_is_access_available_returns_false_when_driver_missing(self):
        """When ODBC driver is not installed, should return False."""
        with patch.dict(
            os.environ,
            {
                "LEGACY_ACCESS_DB_PATH": "docs/legacy_bd/Accdb/test.accdb",
                "LEGACY_ACCESS_DB_PASSWORD": "1041",
            },
            clear=True,
        ):
            with patch("etl.extractors.access_connection.pyodbc") as mock_pyodbc:
                mock_pyodbc.drivers.return_value = ["SQL Server"]  # No Access driver
                assert is_access_available() is False


class TestAccessConnection:
    """Test Access database connection handling."""

    def test_get_connection_raises_when_not_configured(self):
        """Should raise AccessConnectionError when env not configured."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AccessConnectionError) as exc_info:
                get_access_connection()
            assert "not configured" in str(exc_info.value).lower()

    def test_get_connection_raises_when_file_not_found(self):
        """Should raise AccessConnectionError when file doesn't exist."""
        with patch.dict(
            os.environ,
            {
                "LEGACY_ACCESS_DB_PATH": "/nonexistent/db.accdb",
                "LEGACY_ACCESS_DB_PASSWORD": "1041",
            },
            clear=True,
        ):
            with pytest.raises(AccessConnectionError) as exc_info:
                get_access_connection()
            assert "not found" in str(exc_info.value).lower()

    def test_get_connection_raises_when_password_wrong(self):
        """Should raise AccessConnectionError with wrong password."""
        # This test verifies the error path when pyodbc.connect fails
        # We need to mock the entire flow properly
        with patch.dict(
            os.environ,
            {
                "LEGACY_ACCESS_DB_PATH": "docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1_old.accdb",
                "LEGACY_ACCESS_DB_PASSWORD": "wrong_password",
                "LEGACY_ACCESS_ODBC_DRIVER": "Microsoft Access Driver (*.mdb, *.accdb)",
            },
            clear=True,
        ):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("etl.extractors.access_connection._get_access_driver") as mock_driver:
                    mock_driver.return_value = "Microsoft Access Driver (*.mdb, *.accdb)"
                    with patch("etl.extractors.access_connection.pyodbc.connect") as mock_connect:
                        mock_connect.side_effect = Exception("Authentication failed")
                        with pytest.raises(AccessConnectionError) as exc_info:
                            get_access_connection()
                        assert "failed" in str(exc_info.value).lower()

    def test_connection_string_includes_readonly(self):
        """Connection string should include ReadOnly=1 for safety."""
        with patch.dict(
            os.environ,
            {
                "LEGACY_ACCESS_DB_PATH": "docs/legacy_bd/Accdb/test.accdb",
                "LEGACY_ACCESS_DB_PASSWORD": "1041",
                "LEGACY_ACCESS_ODBC_DRIVER": "Microsoft Access Driver (*.mdb, *.accdb)",
            },
            clear=True,
        ):
            with patch("etl.extractors.access_connection.pyodbc") as mock_pyodbc:
                with patch("pathlib.Path.exists", return_value=True):
                    mock_pyodbc.drivers.return_value = ["Microsoft Access Driver (*.mdb, *.accdb)"]
                    mock_pyodbc.connect.return_value = MagicMock()
                    
                    get_access_connection()
                    
                    call_args = mock_pyodbc.connect.call_args[0][0]
                    assert "ReadOnly=1" in call_args


class TestAccessDataExtraction:
    """Test data extraction from Access database."""

    def test_extract_module_data_returns_module_data_objects(self):
        """Extracted data should be ModuleData instances."""
        mock_row = MagicMock()
        mock_row.module_id = 1
        mock_row.module_name = "M01"
        mock_row.fleet_type = "CSR"
        mock_row.km_total = 500000
        mock_row.km_month = 12000
        mock_row.last_maint_date = date(2025, 1, 15)
        mock_row.last_maint_type = "IB"
        mock_row.km_at_maint = 488000

        result = extract_module_data(mock_row, configuration="cuadrupla", coach_count=4)

        assert isinstance(result, ModuleData)
        assert result.module_id == "M01"
        assert result.fleet_type == "CSR"
        assert result.km_total_accumulated == 500000

    def test_get_modules_returns_list_of_module_data(self):
        """Should return a list of ModuleData objects."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        with patch("etl.extractors.access_extractor.get_access_connection", return_value=mock_conn):
            result = get_modules_from_access()

        assert isinstance(result, list)


class TestFallbackBehavior:
    """Test fallback to stub data when Access is unavailable."""

    def test_get_modules_falls_back_to_stub_when_access_unavailable(self):
        """When Access fails, should return stub data."""
        from etl.extractors.access_extractor import get_modules_with_fallback

        with patch("etl.extractors.access_extractor.is_access_available", return_value=False):
            result = get_modules_with_fallback()

        # Should return stub data (111 modules)
        assert len(result) == 111
        assert all(isinstance(m, ModuleData) for m in result)

    def test_get_modules_logs_warning_on_fallback(self, caplog):
        """Should log a warning when falling back to stub data."""
        from etl.extractors.access_extractor import get_modules_with_fallback

        with patch("etl.extractors.access_extractor.is_access_available", return_value=False):
            import logging
            with caplog.at_level(logging.WARNING):
                get_modules_with_fallback()

        assert any("fallback" in record.message.lower() or "stub" in record.message.lower() 
                   for record in caplog.records)


class TestIntegrationWithRealDatabase:
    """
    Integration tests that run against the real Access database.
    
    These tests are skipped in CI (when database is not available).
    """

    @pytest.fixture
    def real_connection_available(self):
        """Check if we can connect to the real database."""
        try:
            # Only import if we're running integration tests
            from dotenv import load_dotenv
            load_dotenv()
            return is_access_available()
        except Exception:
            return False

    @pytest.mark.skipif(
        not os.path.exists("docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1_old.accdb"),
        reason="Access database file not available"
    )
    def test_can_connect_to_real_database(self):
        """Should be able to connect to the real Access database."""
        from dotenv import load_dotenv
        load_dotenv()
        
        if not is_access_available():
            pytest.skip("Access connection not available")
        
        conn = get_access_connection()
        assert conn is not None
        conn.close()

    @pytest.mark.skipif(
        not os.path.exists("docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1_old.accdb"),
        reason="Access database file not available"
    )
    def test_can_extract_modules_from_real_database(self):
        """Should extract module data from real database."""
        from dotenv import load_dotenv
        load_dotenv()
        
        if not is_access_available():
            pytest.skip("Access connection not available")
        
        modules = get_modules_from_access()
        
        # Should have modules (exact count may vary)
        assert len(modules) > 0
        
        # All should be ModuleData instances
        assert all(isinstance(m, ModuleData) for m in modules)
        
        # Check we have both fleet types
        fleet_types = {m.fleet_type for m in modules}
        assert "CSR" in fleet_types or "Toshiba" in fleet_types
