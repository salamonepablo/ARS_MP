"""
URL configuration for ARS_MP project.
"""

import logging
import os

from django.contrib import admin
from django.contrib.auth import authenticate, login, views as auth_views
from django.shortcuts import redirect
from django.urls import include, path

logger = logging.getLogger(__name__)


class DebugLoginView(auth_views.LoginView):
    """Login view with debug logging."""

    def form_valid(self, form):
        logger.warning("LOGIN SUCCESS: user=%s", form.get_user())
        return super().form_valid(form)

    def form_invalid(self, form):
        import os
        from django.conf import settings
        from django.contrib.auth.models import User
        logger.warning("LOGIN FAILED: errors=%s", form.errors)
        logger.warning("DATABASE ENGINE: %s", settings.DATABASES['default']['ENGINE'])
        logger.warning("DATABASE HOST: %s", settings.DATABASES['default'].get('HOST', 'N/A'))
        logger.warning("DATABASE NAME: %s", settings.DATABASES['default'].get('NAME', 'N/A'))
        logger.warning("PGHOST env: %s", os.getenv('PGHOST', 'NOT SET'))
        logger.warning("PGDATABASE env: %s", os.getenv('PGDATABASE', 'NOT SET'))
        logger.warning("USERS IN DB: %s", list(User.objects.values_list('username', flat=True)))
        # Try manual authentication for debugging
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
        user = authenticate(self.request, username=username, password=password)
        logger.warning("MANUAL AUTH: username=%s, result=%s", username, user)
        return super().form_invalid(form)


urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication with debug
    path("accounts/login/", DebugLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    # Fleet app
    path("fleet/", include("web.fleet.urls")),
    # Redirect root to fleet modules
    path("", lambda request: redirect("fleet:module_list")),
]

if os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes") and not os.getenv("RAILWAY_ENVIRONMENT"):
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
