"""
Fleet module views.

Provides views for displaying fleet module cards and KPIs.
"""

from django.shortcuts import render
from django.views.decorators.http import require_GET

from etl.extractors.access_extractor import get_modules_with_fallback

from .stub_data import get_fleet_summary


@require_GET
def module_list(request):
    """
    Display all fleet modules as cards with summary KPIs.

    Data source priority:
    1. Access database (if configured and available)
    2. Stub data (fallback for development/CI)

    URL: /fleet/modules/
    """
    # Get modules from Access or fallback to stub
    modules = get_modules_with_fallback()
    summary = get_fleet_summary(modules)

    # Optional filtering by fleet type
    fleet_filter = request.GET.get("fleet", "all")
    if fleet_filter == "csr":
        modules = [m for m in modules if m.fleet_type == "CSR"]
    elif fleet_filter == "toshiba":
        modules = [m for m in modules if m.fleet_type == "Toshiba"]

    context = {
        "modules": modules,
        "summary": summary,
        "fleet_filter": fleet_filter,
    }

    return render(request, "fleet/module_list.html", context)
