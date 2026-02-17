# Authentication

ARS_MP uses Django's built-in authentication system with Argon2 password hashing.

## How it works

- All fleet views require an active session (`@login_required`).
- Unauthenticated requests are redirected to `/accounts/login/`.
- After successful login, the user is redirected to `/fleet/modules/`.
- Logout redirects back to the login page.

## Password hashing

Passwords are hashed with **Argon2id** (winner of the Password Hashing Competition, recommended by OWASP). PBKDF2 is configured as a fallback for Django's transparent upgrade mechanism.

```python
# config/settings.py
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",  # primary
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",  # fallback
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]
```

Requires `argon2-cffi` package (listed in `requirements.txt`).

## Creating users

### Development (superuser)

```powershell
py manage.py createsuperuser
# Enter: username, email, password
```

### Programmatic user creation

```python
from django.contrib.auth.models import User

User.objects.create_user(
    username="pablo.salamone",
    email="pablo.salamone@trenesargentinos.gob.ar",
    password="secure-password-here",
)
```

### Via Django Admin

Navigate to `http://127.0.0.1:8000/admin/` and log in with a superuser account. Users can be created and managed under "Authentication and Authorization > Users".

## URL routes

| URL | Method | Description |
|-----|--------|-------------|
| `/accounts/login/` | GET/POST | Login form |
| `/accounts/logout/` | POST | Logout (redirects to login) |
| `/admin/` | GET | Django admin (superuser only) |

## Environment variables

No additional environment variables are needed for basic auth. The `SECRET_KEY` in `.env` is used for session signing (already configured).

## Future: SSO / Active Directory

The system is prepared for corporate SSO integration. Django supports multiple authentication backends via `AUTHENTICATION_BACKENDS` in settings. To add LDAP/Active Directory:

1. Install `django-auth-ldap`:
   ```
   pip install django-auth-ldap
   ```

2. Add to `config/settings.py`:
   ```python
   AUTHENTICATION_BACKENDS = [
       "django_auth_ldap.backend.LDAPBackend",
       "django.contrib.auth.backends.ModelBackend",  # fallback
   ]
   ```

3. Configure LDAP server connection via environment variables.

This allows seamless transition from local auth to corporate SSO without changing the view layer.
