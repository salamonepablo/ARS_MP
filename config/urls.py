"""
URL configuration for ARS_MP project.
"""

import logging

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
        logger.warning("LOGIN FAILED: errors=%s", form.errors)
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
    path("__reload__/", include("django_browser_reload.urls")),
    # Redirect root to fleet modules
    path("", lambda request: redirect("fleet:module_list")),
]
