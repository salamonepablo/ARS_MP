"""
Fleet module views.

Provides views for displaying fleet module cards, KPIs,
and detailed module information with maintenance projections.
"""

import logging

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core.services.maintenance_projection import (
    MaintenanceProjectionService,
)
from etl.extractors.access_extractor import (
    get_module_detail_from_access,
    get_modules_with_fallback,
)

from .stub_data import get_fleet_summary

logger = logging.getLogger(__name__)


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


@require_GET
def module_detail(request, module_id: str):
    """
    Display detailed information for a single maintenance module.

    Shows:
    - Module card info (same as list view)
    - Projection of next intervention
    - Key data per cycle type (datos clave para proyección)
    - Maintenance history (last 365 days)

    URL: /fleet/modules/<module_id>/

    When data comes from Access (module_db_id is set), history and
    key_data are loaded on demand from the legacy database.
    """
    # Normalize module_id to uppercase
    module_id = module_id.upper()

    # Get all modules (same data source as list view)
    all_modules = get_modules_with_fallback()

    # Build module lookup and list for dropdown
    module_lookup = {m.module_id: m for m in all_modules}
    module = module_lookup.get(module_id)

    if module is None:
        raise Http404(f"Módulo {module_id} no encontrado")

    # Load detail data on demand if not already populated
    # (Access-sourced modules have module_db_id but empty history/key_data)
    if not module.maintenance_key_data and module.module_db_id is not None:
        logger.info(
            "Loading detail data from Access for %s (db_id=%s)",
            module_id, module.module_db_id,
        )
        history, key_data = get_module_detail_from_access(
            module_db_id=module.module_db_id,
            module_id=module.module_id,
            fleet_type=module.fleet_type,
            km_total=module.km_total_accumulated,
        )
        module.maintenance_history = history
        module.maintenance_key_data = key_data

    # Prepare key data as dicts for the projection service
    key_data_dicts = [
        {
            "cycle_type": kd.cycle_type,
            "cycle_km": kd.cycle_km,
            "km_at_last": kd.km_at_last,
            "last_date": kd.last_date,
        }
        for kd in module.maintenance_key_data
    ]

    # Calculate next intervention projection
    projection = MaintenanceProjectionService.project_next_intervention(
        fleet_type=module.fleet_type,
        km_total=module.km_total_accumulated,
        key_data=key_data_dicts,
    )

    # Module list for the dropdown selector
    module_options = [
        {"id": m.module_id, "label": f"{m.module_id} ({m.fleet_type})"}
        for m in all_modules
    ]

    # Determine data source for display
    # If module_db_id is set, data comes from Access; otherwise from stub
    data_source = "ACCESS" if module.module_db_id is not None else "STUB"

    context = {
        "module": module,
        "projection": projection,
        "module_options": module_options,
        "current_module_id": module_id,
        "data_source": data_source,
    }

    return render(request, "fleet/module_detail.html", context)
