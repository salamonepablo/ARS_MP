"""
Tests for fleet views.

Tests cover:
- Module list view returns correct template
- Module list view provides correct context
- Fleet filtering by CSR/Toshiba
- Module detail view with projection and key data
"""

from unittest.mock import patch

import pytest
from django.test import Client

from web.fleet.stub_data import get_all_modules


@pytest.mark.django_db
class TestModuleListView:
    """Tests for the module_list view."""

    @pytest.fixture
    def client(self):
        """Provide Django test client."""
        return Client()

    @pytest.fixture
    def mock_stub_data(self):
        """
        Mock the data source to use stub data.
        
        This ensures tests are deterministic and don't depend on
        the Access database being available.
        """
        with patch(
            "web.fleet.views.get_modules_with_fallback",
            return_value=get_all_modules()
        ):
            yield

    def test_view_returns_200(self, client):
        """Module list view should return HTTP 200."""
        response = client.get("/fleet/modules/")
        assert response.status_code == 200

    def test_view_uses_correct_template(self, client):
        """View should use fleet/module_list.html template."""
        response = client.get("/fleet/modules/")
        assert "fleet/module_list.html" in [t.name for t in response.templates]

    def test_context_contains_modules(self, client, mock_stub_data):
        """Context should contain 'modules' list with 111 modules (stub data)."""
        response = client.get("/fleet/modules/")
        assert "modules" in response.context
        assert len(response.context["modules"]) == 111

    def test_context_contains_summary(self, client, mock_stub_data):
        """Context should contain 'summary' dict with KPIs."""
        response = client.get("/fleet/modules/")
        assert "summary" in response.context
        
        summary = response.context["summary"]
        assert summary["total_count"] == 111
        assert summary["csr_count"] == 86
        assert summary["toshiba_count"] == 25

    def test_context_contains_fleet_filter(self, client):
        """Context should contain current fleet filter value."""
        response = client.get("/fleet/modules/")
        assert "fleet_filter" in response.context
        assert response.context["fleet_filter"] == "all"

    def test_filter_by_csr(self, client, mock_stub_data):
        """Filtering by CSR should return only CSR modules."""
        response = client.get("/fleet/modules/?fleet=csr")
        
        assert response.context["fleet_filter"] == "csr"
        modules = response.context["modules"]
        assert len(modules) == 86
        for module in modules:
            assert module.fleet_type == "CSR"

    def test_filter_by_toshiba(self, client, mock_stub_data):
        """Filtering by Toshiba should return only Toshiba modules."""
        response = client.get("/fleet/modules/?fleet=toshiba")
        
        assert response.context["fleet_filter"] == "toshiba"
        modules = response.context["modules"]
        assert len(modules) == 25
        for module in modules:
            assert module.fleet_type == "Toshiba"

    def test_only_get_method_allowed(self, client):
        """View should only allow GET requests."""
        response = client.post("/fleet/modules/")
        assert response.status_code == 405  # Method Not Allowed


@pytest.mark.django_db
class TestModuleListViewWithRealData:
    """
    Integration tests that use real data source.
    
    These tests verify the view works with whatever data is available,
    without checking specific counts.
    """

    @pytest.fixture
    def client(self):
        """Provide Django test client."""
        return Client()

    def test_view_returns_modules_list(self, client):
        """View should return a non-empty list of modules."""
        response = client.get("/fleet/modules/")
        modules = response.context["modules"]
        
        # Should have some modules (either from Access or stub)
        assert len(modules) > 0
        
    def test_all_modules_have_required_attributes(self, client):
        """All modules should have the required attributes."""
        response = client.get("/fleet/modules/")
        modules = response.context["modules"]
        
        for module in modules:
            assert hasattr(module, "module_id")
            assert hasattr(module, "fleet_type")
            assert hasattr(module, "km_total_accumulated")
            assert hasattr(module, "last_maintenance_date")

    def test_summary_has_required_keys(self, client):
        """Summary should contain all required KPI keys."""
        response = client.get("/fleet/modules/")
        summary = response.context["summary"]
        
        required_keys = [
            "csr_count", "toshiba_count", "total_count",
            "csr_km_month", "toshiba_km_month", "total_km_month",
            "csr_km_total", "toshiba_km_total", "total_km_total",
        ]
        for key in required_keys:
            assert key in summary


@pytest.mark.django_db
class TestModuleDetailView:
    """Tests for the module_detail view."""

    @pytest.fixture
    def client(self):
        """Provide Django test client."""
        return Client()

    @pytest.fixture
    def mock_stub_data(self):
        """Mock data source to use stub data."""
        with patch(
            "web.fleet.views.get_modules_with_fallback",
            return_value=get_all_modules()
        ):
            yield

    def test_detail_returns_200_for_csr(self, client, mock_stub_data):
        """Detail view should return 200 for a valid CSR module."""
        response = client.get("/fleet/modules/M01/")
        assert response.status_code == 200

    def test_detail_returns_200_for_toshiba(self, client, mock_stub_data):
        """Detail view should return 200 for a valid Toshiba module."""
        response = client.get("/fleet/modules/T01/")
        assert response.status_code == 200

    def test_detail_returns_404_for_invalid(self, client, mock_stub_data):
        """Detail view should return 404 for non-existent module."""
        response = client.get("/fleet/modules/X99/")
        assert response.status_code == 404

    def test_detail_case_insensitive(self, client, mock_stub_data):
        """Module ID should be case-insensitive."""
        response = client.get("/fleet/modules/m01/")
        assert response.status_code == 200

    def test_detail_uses_correct_template(self, client, mock_stub_data):
        """Should use fleet/module_detail.html template."""
        response = client.get("/fleet/modules/M01/")
        template_names = [t.name for t in response.templates]
        assert "fleet/module_detail.html" in template_names

    def test_detail_context_has_module(self, client, mock_stub_data):
        """Context should contain the module object."""
        response = client.get("/fleet/modules/M01/")
        assert "module" in response.context
        module = response.context["module"]
        assert module.module_id == "M01"
        assert module.fleet_type == "CSR"

    def test_detail_context_has_projection(self, client, mock_stub_data):
        """Context should contain a projection result."""
        response = client.get("/fleet/modules/M01/")
        assert "projection" in response.context
        projection = response.context["projection"]
        # With stub data, projection should be computed
        assert projection is not None
        assert hasattr(projection, "cycle_type")
        assert hasattr(projection, "km_remaining")
        assert hasattr(projection, "estimated_date")

    def test_detail_context_has_module_options(self, client, mock_stub_data):
        """Context should contain module_options for the dropdown."""
        response = client.get("/fleet/modules/M01/")
        assert "module_options" in response.context
        options = response.context["module_options"]
        assert len(options) == 111  # 86 CSR + 25 Toshiba

    def test_detail_module_has_key_data(self, client, mock_stub_data):
        """Module should have maintenance_key_data populated."""
        response = client.get("/fleet/modules/M01/")
        module = response.context["module"]
        assert len(module.maintenance_key_data) > 0
        # CSR should have 4 cycle types
        assert len(module.maintenance_key_data) == 4

    def test_detail_toshiba_has_key_data(self, client, mock_stub_data):
        """Toshiba module should have 2 key data entries (RB, RG)."""
        response = client.get("/fleet/modules/T01/")
        module = response.context["module"]
        assert len(module.maintenance_key_data) == 2

    def test_detail_module_has_history(self, client, mock_stub_data):
        """Module should have maintenance_history populated."""
        response = client.get("/fleet/modules/M01/")
        module = response.context["module"]
        assert len(module.maintenance_history) > 0

    def test_detail_context_has_data_source(self, client, mock_stub_data):
        """Context should contain data_source indicator."""
        response = client.get("/fleet/modules/M01/")
        assert "data_source" in response.context
        # With stub data, module_db_id is None, so source is STUB
        assert response.context["data_source"] == "STUB"

    def test_detail_only_get_allowed(self, client):
        """Detail view should only allow GET requests."""
        response = client.post("/fleet/modules/M01/")
        assert response.status_code == 405
