"""
Tests for fleet views.

Tests cover:
- Module list view returns correct template
- Module list view provides correct context
- Fleet filtering by CSR/Toshiba
"""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestModuleListView:
    """Tests for the module_list view."""

    @pytest.fixture
    def client(self):
        """Provide Django test client."""
        return Client()

    def test_view_returns_200(self, client):
        """Module list view should return HTTP 200."""
        response = client.get("/fleet/modules/")
        assert response.status_code == 200

    def test_view_uses_correct_template(self, client):
        """View should use fleet/module_list.html template."""
        response = client.get("/fleet/modules/")
        assert "fleet/module_list.html" in [t.name for t in response.templates]

    def test_context_contains_modules(self, client):
        """Context should contain 'modules' list."""
        response = client.get("/fleet/modules/")
        assert "modules" in response.context
        assert len(response.context["modules"]) == 111

    def test_context_contains_summary(self, client):
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

    def test_filter_by_csr(self, client):
        """Filtering by CSR should return only CSR modules."""
        response = client.get("/fleet/modules/?fleet=csr")
        
        assert response.context["fleet_filter"] == "csr"
        modules = response.context["modules"]
        assert len(modules) == 86
        for module in modules:
            assert module.fleet_type == "CSR"

    def test_filter_by_toshiba(self, client):
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
