"""
Pytest configuration and fixtures for ARS_MP tests.
"""

import pytest
from datetime import date
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def sample_module_data():
    """Provide sample data for testing ModuleData."""
    from web.fleet.stub_data import ModuleData

    return ModuleData(
        module_id="M01",
        module_number=1,
        fleet_type="CSR",
        configuration="cuadrupla",
        coach_count=4,
        km_current_month=10000,
        km_total_accumulated=500000,
        last_maintenance_date=date(2025, 1, 1),
        last_maintenance_type="IQ",
        km_at_last_maintenance=450000,
    )


@pytest.fixture
def csr_modules():
    """Provide CSR modules for testing."""
    from web.fleet.stub_data import generate_csr_modules
    import random

    random.seed(42)
    return generate_csr_modules()


@pytest.fixture
def toshiba_modules():
    """Provide Toshiba modules for testing."""
    from web.fleet.stub_data import generate_toshiba_modules
    import random

    random.seed(42)
    return generate_toshiba_modules()


@pytest.fixture
def all_modules():
    """Provide all modules for testing."""
    from web.fleet.stub_data import get_all_modules

    return get_all_modules()


@pytest.fixture
def auth_user(db):
    """Create a test user for authentication."""
    return User.objects.create_user(
        username="analista",
        password="testpass123!",
        email="analista@trenesargentinos.gob.ar",
    )


@pytest.fixture
def authenticated_client(auth_user):
    """Provide a Django test client with an authenticated session."""
    client = Client()
    client.login(username="analista", password="testpass123!")
    return client
