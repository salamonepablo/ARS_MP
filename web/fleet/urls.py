"""Fleet app URL configuration."""

from django.urls import path

from . import views

app_name = "fleet"

urlpatterns = [
    path("modules/", views.module_list, name="module_list"),
    path("modules/<str:module_id>/", views.module_detail, name="module_detail"),
    # Sync Access → Postgres
    path("sync/status/", views.sync_status, name="sync_status"),
    path("sync/trigger/", views.sync_trigger, name="sync_trigger"),
]
