"""Fleet app URL configuration."""

from django.urls import path

from . import views

app_name = "fleet"

urlpatterns = [
    path("modules/", views.module_list, name="module_list"),
]
