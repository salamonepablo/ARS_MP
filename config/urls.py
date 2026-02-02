"""
URL configuration for ARS_MP project.
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("fleet/", include("web.fleet.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    # Redirect root to fleet modules
    path("", lambda request: redirect("fleet:module_list")),
]
