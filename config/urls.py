"""
URL configuration for ARS_MP project.
"""

import os

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    # Fleet app
    path("fleet/", include("web.fleet.urls")),
    # Redirect root to fleet modules
    path("", lambda request: redirect("fleet:module_list")),
]

if os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes") and not os.getenv("RAILWAY_ENVIRONMENT"):
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
