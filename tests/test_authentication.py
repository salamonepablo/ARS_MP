"""
Tests de autenticacion y proteccion de vistas.

Verifican que:
- Vistas protegidas redirigen a login cuando no hay sesion activa.
- Usuarios autenticados acceden normalmente.
- El formulario de login funciona correctamente.
- Logout redirige al login.
"""

from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.test import Client

from web.fleet.stub_data import get_all_modules


@pytest.mark.django_db
class TestUnauthenticatedRedirects:
    """Vistas protegidas deben redirigir a /accounts/login/ sin sesion."""

    @pytest.fixture
    def client(self):
        return Client()

    def test_module_list_redirects_to_login(self, client):
        """GET /fleet/modules/ sin sesion redirige a login."""
        response = client.get("/fleet/modules/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_module_detail_redirects_to_login(self, client):
        """GET /fleet/modules/M01/ sin sesion redirige a login."""
        response = client.get("/fleet/modules/M01/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_projection_grid_redirects_to_login(self, client):
        """GET /fleet/planner/ sin sesion redirige a login."""
        response = client.get("/fleet/planner/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_projection_export_redirects_to_login(self, client):
        """GET /fleet/planner/export/ sin sesion redirige a login."""
        response = client.get("/fleet/planner/export/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_sync_status_redirects_to_login(self, client):
        """GET /fleet/sync/status/ sin sesion redirige a login."""
        response = client.get("/fleet/sync/status/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_root_redirects_to_login(self, client):
        """GET / sin sesion redirige (via fleet) a login."""
        response = client.get("/", follow=True)
        # Should end up at login page after redirect chain
        assert response.status_code == 200
        assert "/accounts/login/" in response.request["PATH_INFO"]


@pytest.mark.django_db
class TestAuthenticatedAccess:
    """Usuarios autenticados acceden normalmente a las vistas."""

    @pytest.fixture
    def authenticated_client(self):
        user = User.objects.create_user(
            username="analista",
            password="testpass123!",
            email="analista@trenesargentinos.gob.ar",
        )
        client = Client()
        client.login(username="analista", password="testpass123!")
        return client

    @pytest.fixture
    def mock_stub_data(self):
        with patch(
            "web.fleet.views.get_modules_with_fallback",
            return_value=get_all_modules(),
        ):
            yield

    def test_module_list_returns_200(self, authenticated_client, mock_stub_data):
        """GET /fleet/modules/ con sesion retorna 200."""
        response = authenticated_client.get("/fleet/modules/")
        assert response.status_code == 200

    def test_projection_grid_returns_200(self, authenticated_client, mock_stub_data):
        """GET /fleet/planner/ con sesion retorna 200."""
        response = authenticated_client.get("/fleet/planner/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestLoginFlow:
    """Tests del flujo de login/logout."""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="analista",
            password="testpass123!",
            email="analista@trenesargentinos.gob.ar",
        )

    @pytest.fixture
    def client(self):
        return Client()

    def test_login_page_returns_200(self, client):
        """GET /accounts/login/ retorna 200 y el formulario."""
        response = client.get("/accounts/login/")
        assert response.status_code == 200

    def test_login_with_valid_credentials(self, client, user):
        """POST con credenciales validas redirige a la flota."""
        response = client.post("/accounts/login/", {
            "username": "analista",
            "password": "testpass123!",
        })
        assert response.status_code == 302
        assert response.url == "/fleet/modules/"

    def test_login_with_invalid_credentials(self, client, user):
        """POST con credenciales invalidas muestra error."""
        response = client.post("/accounts/login/", {
            "username": "analista",
            "password": "wrongpassword",
        })
        assert response.status_code == 200  # Re-renders form

    def test_logout_redirects_to_login(self, client, user):
        """POST /accounts/logout/ redirige al login."""
        client.login(username="analista", password="testpass123!")
        response = client.post("/accounts/logout/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url


@pytest.mark.django_db
class TestPasswordHashing:
    """Verificar que las contrasenas se almacenan con hashing robusto."""

    def test_password_is_hashed(self):
        """La contrasena no se almacena en texto plano."""
        user = User.objects.create_user(
            username="testuser",
            password="mypassword123!",
        )
        assert user.password != "mypassword123!"
        assert user.password.startswith(("argon2", "pbkdf2_sha256"))

    def test_check_password_works(self):
        """check_password valida correctamente."""
        user = User.objects.create_user(
            username="testuser",
            password="mypassword123!",
        )
        assert user.check_password("mypassword123!") is True
        assert user.check_password("wrongpassword") is False
