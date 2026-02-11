"""
Fleet module views.

Provides views for displaying fleet module cards, KPIs,
detailed module information with maintenance projections,
and sync controls for the Access-to-Postgres ETL.
"""

import logging
import subprocess
import sys

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from core.services.maintenance_projection import (
    MaintenanceProjectionService,
)
from etl.extractors.access_extractor import (
    get_module_detail_from_access,
    get_modules_with_fallback,
)
from etl.extractors.postgres_extractor import (
    get_module_detail_from_postgres,
    is_postgres_staging_available,
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

    # Sync status for the sync bar
    from infrastructure.database.models import SyncLog
    latest_sync = SyncLog.objects.first()  # ordered by -started_at

    context = {
        "modules": modules,
        "summary": summary,
        "fleet_filter": fleet_filter,
        "latest_sync": latest_sync,
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
        # Prefer Postgres staging; fall back to live ODBC
        if is_postgres_staging_available():
            logger.info(
                "Loading detail data from Postgres for %s (db_id=%s)",
                module_id, module.module_db_id,
            )
            history, key_data = get_module_detail_from_postgres(
                module_db_id=module.module_db_id,
                module_id=module.module_id,
                fleet_type=module.fleet_type,
                km_total=module.km_total_accumulated,
                commissioning_date=module.reference_date,
            )
        else:
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
    if module.module_db_id is not None:
        data_source = "POSTGRES" if is_postgres_staging_available() else "ACCESS"
    else:
        data_source = "STUB"

    context = {
        "module": module,
        "projection": projection,
        "module_options": module_options,
        "current_module_id": module_id,
        "data_source": data_source,
    }

    return render(request, "fleet/module_detail.html", context)


# ---------------------------------------------------------------------------
# Sync Access → Postgres
# ---------------------------------------------------------------------------

@require_GET
def sync_status(request):
    """
    Return JSON with the latest sync status for Alpine.js polling.

    URL: /fleet/sync/status/
    """
    from infrastructure.database.models import SyncLog

    latest = SyncLog.objects.first()  # ordered by -started_at
    if latest is None:
        return JsonResponse({
            "has_synced": False,
            "status": "never",
            "started_at": None,
            "finished_at": None,
            "duration": None,
            "tables": {},
            "error": "",
        })

    return JsonResponse({
        "has_synced": True,
        "status": latest.status,
        "started_at": latest.started_at.isoformat() if latest.started_at else None,
        "finished_at": latest.finished_at.isoformat() if latest.finished_at else None,
        "duration": latest.duration_seconds,
        "tables": latest.tables_synced or {},
        "error": latest.error_message or "",
    })


@require_POST
def sync_trigger(request):
    """
    Launch ``sync_access`` as a detached subprocess and return immediately.

    The subprocess writes its progress into a ``SyncLog`` row that the
    frontend polls via ``/fleet/sync/status/``.

    URL: POST /fleet/sync/trigger/
    """
    from infrastructure.database.models import SyncLog

    # Prevent concurrent syncs
    running = SyncLog.objects.filter(status="running").exists()
    if running:
        return JsonResponse(
            {"ok": False, "error": "Ya hay una sincronización en curso."},
            status=409,
        )

    # Launch sync_access as a detached subprocess
    python_exe = sys.executable  # same interpreter running Django
    cmd = [python_exe, "manage.py", "sync_access"]

    logger.info("Launching sync_access subprocess: %s", " ".join(cmd))

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            # On Windows, CREATE_NO_WINDOW prevents a console flash
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if sys.platform == "win32"
                else 0
            ),
        )
    except Exception as e:
        logger.exception("Failed to launch sync_access subprocess")
        return JsonResponse(
            {"ok": False, "error": f"Error al lanzar sync: {e}"},
            status=500,
        )

    return JsonResponse({"ok": True})
