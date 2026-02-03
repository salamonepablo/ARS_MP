"""
Tests for fleet views.

Tests cover:
- Module list view returns correct template
- Module list view provides correct context
- Fleet filtering by CSR/Toshiba
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
