"""
Postgres staging data extractor for fleet modules.

Reads from the ``stg_*`` tables populated by ``sync_access`` and assembles
the same ``ModuleData`` / ``MaintenanceEvent`` / ``MaintenanceKeyData`` objects
that the web views expect.

This module **replaces** the live ODBC path (``access_extractor.py``) at
request time.  The ODBC connection is only needed by ``sync_access`` now.

Design decision (see docs/decisions/access_to_postgres_staging.md):
  Access = source system, synced periodically via ``sync_access``.
  Postgres = operational data store, queried by Django views.
"""

import logging
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Literal, Optional

from django.db.models import Max, Min, Q, Subquery, OuterRef

from core.services.maintenance_projection import (
    CSR_HEAVY_CYCLES,
    CSR_HIERARCHY,
    CSR_MAINTENANCE_CYCLES,
    TASK_TO_CYCLE,
    TOSHIBA_HEAVY_CYCLES,
    TOSHIBA_HIERARCHY,
    TOSHIBA_MAINTENANCE_CYCLES,
)
from infrastructure.database.models import (
    StgCoche,
    StgFormacionModulo,
    StgKilometraje,
    StgModulo,
    StgOtSimaf,
)
from web.fleet.stub_data import (
    CoachInfo,
    MaintenanceEvent,
    MaintenanceKeyData,
    ModuleData,
)

from .access_extractor import get_rg_reference_dates

logger = logging.getLogger("etl")


# ---------------------------------------------------------------------------
# Helpers (shared logic ported from access_extractor)
# ---------------------------------------------------------------------------

def _normalize_module_id(value: Optional[str]) -> str:
    """Normalize module identifiers to zero-padded format (e.g., 'M01')."""
    if not value:
        return ""
    raw = str(value).strip().upper()
    match = re.search(r"([A-Z])\s*0*(\d+)", raw)
    if match:
        prefix = match.group(1)
        try:
            num = int(match.group(2))
        except ValueError:
            return raw
        return f"{prefix}{num:02d}"
    return raw


def _determine_fleet_type(
    tipo_mr: Optional[str],
    marca_mr: Optional[str],
    module_name: str,
) -> str:
    """Determine fleet type from vehicle class or module name."""
    if marca_mr:
        marca_upper = marca_mr.upper()
        if "CSR" in marca_upper:
            return "CSR"
        if "TOSHIBA" in marca_upper:
            return "Toshiba"
    if module_name:
        name_upper = module_name.upper().strip()
        if name_upper.startswith("M"):
            return "CSR"
        if name_upper.startswith("T"):
            return "Toshiba"
    logger.warning(
        "Could not determine fleet type for module %s, defaulting to CSR",
        module_name,
    )
    return "CSR"


def _determine_configuration(module_name: str, fleet_type: str) -> tuple[str, int]:
    """Determine module configuration (tripla/cuadrupla) and coach count."""
    try:
        num_str = "".join(c for c in module_name if c.isdigit())
        module_num = int(num_str) if num_str else 0
    except ValueError:
        module_num = 0

    if fleet_type == "CSR":
        if module_num <= 42:
            return "cuadrupla", 4
        return "tripla", 3
    else:
        toshiba_cuadruplas = {6, 11, 12, 16, 20, 24, 29, 31, 34, 39, 45, 52}
        if module_num in toshiba_cuadruplas:
            return "cuadrupla", 4
        return "tripla", 3


def _ubicacion_to_coach_type(ubicacion: Optional[str]) -> str:
    """Convert Ubicación field to standard coach type code."""
    if not ubicacion:
        return "?"
    ubic = ubicacion.strip().upper()
    if ubic in ("MC1", "MC2", "R1", "R2", "MC", "M", "R", "RP"):
        if ubic == "MC":
            return "M"
        return ubic
    return "?"


def _ubicacion_sort_key(ubicacion: Optional[str], fleet_type: str) -> int:
    """Sort key for coach ordering based on physical EMU position."""
    if not ubicacion:
        return 99
    ubic = ubicacion.strip().upper()
    if fleet_type == "CSR":
        order = {"MC1": 1, "R1": 2, "R2": 3, "MC2": 4}
    else:
        order = {"MC": 1, "M": 1, "R": 2, "RP": 3}
    return order.get(ubic, 99)


# ---------------------------------------------------------------------------
# Availability check
# ---------------------------------------------------------------------------

def is_postgres_staging_available() -> bool:
    """
    Check whether the Postgres staging tables have been populated.

    Returns True if ``stg_modulo`` has at least one row.
    """
    try:
        return StgModulo.objects.exists()
    except Exception:
        return False


# ---------------------------------------------------------------------------
# List view: get_modules_from_postgres
# ---------------------------------------------------------------------------

def get_modules_from_postgres() -> list[ModuleData]:
    """
    Build the full module list from Postgres staging tables.

    Replicates the logic of ``access_extractor.get_modules_from_access()``
    but queries Django ORM models instead of raw ODBC.

    Returns:
        List of ModuleData objects for all active modules.
    """
    # ------------------------------------------------------------------
    # 1. Load all staging data in bulk (minimize DB round-trips)
    # ------------------------------------------------------------------

    # Modules
    stg_modules = list(StgModulo.objects.all())
    module_id_to_name = {
        m.access_id: _normalize_module_id(m.nombre)
        for m in stg_modules
        if m.nombre
    }

    # RG dates from internalized reference data
    rg_dates = get_rg_reference_dates()

    # Latest km per module: subquery for max fecha per modulo
    latest_km_qs = (
        StgKilometraje.objects
        .filter(kilometraje__isnull=False)
        .values("modulo_access_id")
        .annotate(max_fecha=Max("fecha"))
    )
    latest_km_map: dict[int, tuple[int, date]] = {}
    for entry in latest_km_qs:
        mid = entry["modulo_access_id"]
        max_f = entry["max_fecha"]
        row = (
            StgKilometraje.objects
            .filter(
                modulo_access_id=mid,
                fecha=max_f,
                kilometraje__isnull=False,
            )
            .order_by("-kilometraje")
            .first()
        )
        if row:
            latest_km_map[mid] = (row.kilometraje, row.fecha)

    # Global max km date
    global_max_fecha = (
        StgKilometraje.objects
        .filter(kilometraje__isnull=False)
        .aggregate(max_fecha=Max("fecha"))
    )["max_fecha"]

    # Month window km (min/max within the calendar month of global_max_fecha)
    km_month_data: dict[int, int] = {}  # modulo_access_id -> km_month
    if global_max_fecha:
        month_start = date(global_max_fecha.year, global_max_fecha.month, 1)
        month_agg = (
            StgKilometraje.objects
            .filter(
                fecha__gte=month_start,
                fecha__lte=global_max_fecha,
                kilometraje__isnull=False,
            )
            .values("modulo_access_id")
            .annotate(
                min_km=Min("kilometraje"),
                max_km=Max("kilometraje"),
            )
        )
        for entry in month_agg:
            mid = entry["modulo_access_id"]
            min_km = entry["min_km"]
            max_km = entry["max_km"]
            if min_km is not None and max_km is not None:
                km_month_data[mid] = max(0, max_km - min_km)

    # Last maintenance event per module (for the relevant task types)
    relevant_tasks = list(TASK_TO_CYCLE.keys())
    maint_latest_qs = (
        StgOtSimaf.objects
        .filter(tarea__in=relevant_tasks, fecha_fin__isnull=False)
        .values("modulo_access_id")
        .annotate(max_fecha=Max("fecha_fin"))
    )
    maint_data: dict[int, tuple[str, date, int]] = {}  # mid -> (tarea, fecha_fin, km)
    for entry in maint_latest_qs:
        mid = entry["modulo_access_id"]
        max_f = entry["max_fecha"]
        row = (
            StgOtSimaf.objects
            .filter(
                modulo_access_id=mid,
                fecha_fin=max_f,
                tarea__in=relevant_tasks,
            )
            .first()
        )
        if row:
            maint_data[mid] = (row.tarea, row.fecha_fin, row.km or 0)

    # Last RG per module
    rg_latest_qs = (
        StgOtSimaf.objects
        .filter(tarea="RG", fecha_fin__isnull=False)
        .values("modulo_access_id")
        .annotate(max_fecha=Max("fecha_fin"))
    )
    rg_data: dict[int, tuple[date, int]] = {}
    for entry in rg_latest_qs:
        mid = entry["modulo_access_id"]
        max_f = entry["max_fecha"]
        row = (
            StgOtSimaf.objects
            .filter(modulo_access_id=mid, tarea="RG", fecha_fin=max_f)
            .first()
        )
        if row:
            rg_data[mid] = (row.fecha_fin, row.km or 0)

    # Coach composition per module
    coaches_by_module: dict[int, list[CoachInfo]] = defaultdict(list)
    form_rows = (
        StgFormacionModulo.objects
        .select_related()
        .all()
        .values_list("modulo_access_id", "coche", named=True)
    )
    # Build coche lookup for ubicacion
    coche_ubic: dict[int, str] = {}
    for c in StgCoche.objects.all():
        coche_ubic[c.coche] = c.ubicacion or ""

    # Group by module, sort by ubicacion
    raw_coaches: dict[int, list[tuple[int, CoachInfo]]] = defaultdict(list)
    for fm in form_rows:
        mid = fm.modulo_access_id
        coche_num = fm.coche
        ubicacion = coche_ubic.get(coche_num, "")
        module_name = module_id_to_name.get(mid, "")
        fleet_type = "CSR" if module_name.startswith("M") else "Toshiba"
        coach_type = _ubicacion_to_coach_type(ubicacion)
        sort_key = _ubicacion_sort_key(ubicacion, fleet_type)
        raw_coaches[mid].append((sort_key, CoachInfo(number=coche_num, coach_type=coach_type)))

    for mid, coach_tuples in raw_coaches.items():
        sorted_coaches = sorted(coach_tuples, key=lambda x: x[0])
        coaches_by_module[mid] = [coach for _, coach in sorted_coaches]

    # ------------------------------------------------------------------
    # 2. Build ModuleData objects
    # ------------------------------------------------------------------
    modules: list[ModuleData] = []

    for stg in stg_modules:
        module_name = _normalize_module_id(stg.nombre)
        if not module_name or module_name in ("M00", "T00"):
            continue

        fleet_type = _determine_fleet_type(stg.tipo_mr, stg.marca_mr, module_name)
        configuration, coach_count = _determine_configuration(module_name, fleet_type)

        # Extract module number
        num_str = "".join(c for c in module_name if c.isdigit())
        module_number = int(num_str) if num_str else 0
        prefix = "M" if fleet_type == "CSR" else "T"
        module_id = f"{prefix}{module_number:02d}"

        # KM data
        km_entry = latest_km_map.get(stg.access_id)
        km_total = km_entry[0] if km_entry else 0
        km_current_month_date = (
            global_max_fecha if global_max_fecha
            else (km_entry[1] if km_entry else None)
        )

        # KM month
        km_month = km_month_data.get(stg.access_id, 0)

        # Maintenance data
        maint_entry = maint_data.get(stg.access_id)
        if maint_entry:
            last_maint_type, last_maint_date, km_at_maint = maint_entry
        else:
            last_maint_type = "N/A"
            last_maint_date = date.today()
            km_at_maint = 0

        # RG data
        rg_entry = rg_data.get(stg.access_id)
        last_rg_date = rg_entry[0] if rg_entry else None
        km_at_last_rg = rg_entry[1] if rg_entry else None

        # RG dates from CSV
        reference_date = None
        reference_type = ""
        if module_id in rg_dates:
            reference_date, reference_type = rg_dates[module_id]

        # Coaches
        coaches = coaches_by_module.get(stg.access_id, [])

        fleet_type_literal: Literal["CSR", "Toshiba"] = (
            "CSR" if fleet_type == "CSR" else "Toshiba"
        )
        config_literal: Literal["tripla", "cuadrupla"] = (
            "cuadrupla" if configuration == "cuadrupla" else "tripla"
        )

        modules.append(ModuleData(
            module_id=module_id,
            module_number=module_number,
            fleet_type=fleet_type_literal,
            configuration=config_literal,
            coach_count=coach_count,
            km_current_month=km_month,
            km_total_accumulated=km_total,
            last_maintenance_date=last_maint_date,
            last_maintenance_type=str(last_maint_type),
            km_at_last_maintenance=km_at_maint,
            module_db_id=stg.access_id,
            coaches=coaches,
            reference_date=reference_date,
            reference_type=reference_type,
            km_current_month_date=km_current_month_date,
            last_rg_date=last_rg_date,
            km_at_last_rg=km_at_last_rg,
        ))

    logger.info("Loaded %d modules from Postgres staging tables", len(modules))
    return modules


# ---------------------------------------------------------------------------
# Detail view: get_module_detail_from_postgres
# ---------------------------------------------------------------------------

def get_module_detail_from_postgres(
    module_db_id: int,
    module_id: str,
    fleet_type: str,
    km_total: int,
    commissioning_date: Optional[date] = None,
) -> tuple[list[MaintenanceEvent], list[MaintenanceKeyData]]:
    """
    Load maintenance history and key cycle data from Postgres staging.

    Replicates ``access_extractor.get_module_detail_from_access()`` but
    reads from ``StgOtSimaf`` instead of live ODBC.

    Args:
        module_db_id: Numeric FK (``StgModulo.access_id``).
        module_id: Human-readable module id (e.g. "M04").
        fleet_type: "CSR" or "Toshiba".
        km_total: Current total accumulated km.
        commissioning_date: Date of commissioning (puesta en servicio).
            Used as fallback for DA/RG when no intervention recorded.

    Returns:
        Tuple of (history, key_data).
    """
    history: list[MaintenanceEvent] = []
    key_data: list[MaintenanceKeyData] = []

    # 1. Determine cutoff date (365 days before the latest OT for this module)
    max_fecha = (
        StgOtSimaf.objects
        .filter(modulo_access_id=module_db_id, fecha_fin__isnull=False)
        .aggregate(max_f=Max("fecha_fin"))
    )["max_f"]

    reference_date = max_fecha or date.today()
    cutoff_date = reference_date - timedelta(days=365)

    # 2. History: all OTs in the last 365 days for this module
    ot_rows = (
        StgOtSimaf.objects
        .filter(
            modulo_access_id=module_db_id,
            fecha_fin__gte=cutoff_date,
        )
        .order_by("-fecha_fin")
    )

    for ot in ot_rows:
        if ot.fecha_fin is None:
            continue

        start_date = ot.fecha_inicio
        end_date = ot.fecha_fin
        duration_days = None
        if start_date and end_date:
            duration_days = (end_date - start_date).days

        history.append(MaintenanceEvent(
            event_date=end_date,
            start_date=start_date,
            end_date=end_date,
            task_type=ot.tarea or "",
            km_at_event=ot.km or 0,
            ot_simaf=ot.ot_simaf or "",
            duration_days=duration_days,
        ))

    logger.info(
        "Module %s (db_id=%s): loaded %d history events from Postgres "
        "(cutoff=%s, ref_date=%s)",
        module_id, module_db_id, len(history), cutoff_date, reference_date,
    )

    # 3. Key data per cycle type: find latest OT for each task code
    all_ots = (
        StgOtSimaf.objects
        .filter(modulo_access_id=module_db_id)
        .exclude(tarea__isnull=True)
        .exclude(tarea="")
    )

    # Select cycles and hierarchy based on fleet type
    # Use ALL cycles for projection, but HEAVY cycles for display table
    if fleet_type == "CSR":
        all_cycles = CSR_MAINTENANCE_CYCLES
        heavy_cycles = CSR_HEAVY_CYCLES
        hierarchy = CSR_HIERARCHY
    else:
        all_cycles = TOSHIBA_MAINTENANCE_CYCLES
        heavy_cycles = TOSHIBA_HEAVY_CYCLES
        hierarchy = TOSHIBA_HIERARCHY

    # Build lookup: task -> (latest_date, km)
    latest_by_task: dict[str, tuple[Optional[date], int]] = {}
    for ot in all_ots:
        task = (ot.tarea or "").strip().upper()
        if not task:
            continue
        d = ot.fecha_fin
        km = ot.km or 0

        if task not in latest_by_task:
            latest_by_task[task] = (d, km)
        else:
            existing_date, _ = latest_by_task[task]
            if d and (existing_date is None or d > existing_date):
                latest_by_task[task] = (d, km)

    # Aggregate by cycle type (raw data before inheritance)
    latest_by_cycle: dict[str, dict] = {}
    for task, (d, km) in latest_by_task.items():
        cycle = TASK_TO_CYCLE.get(task)
        if cycle is None:
            continue
        # Only consider cycles relevant to this fleet
        if cycle not in hierarchy:
            continue

        if cycle not in latest_by_cycle:
            latest_by_cycle[cycle] = {
                "last_date": d,
                "km_at_last": km,
                "inherited_from": None,
            }
        else:
            existing_date = latest_by_cycle[cycle]["last_date"]
            if d and (existing_date is None or d > existing_date):
                latest_by_cycle[cycle] = {
                    "last_date": d,
                    "km_at_last": km,
                    "inherited_from": None,
                }

    # Apply commissioning_date as fallback for top-level cycle BEFORE inheritance
    # This ensures DA/RG gets the puesta en servicio date, which then propagates
    # to lower cycles (PE, BA, AN for CSR; RB, MEN for Toshiba) via inheritance.
    top_cycle = "DA" if fleet_type == "CSR" else "RG"
    if top_cycle not in latest_by_cycle and commissioning_date:
        latest_by_cycle[top_cycle] = {
            "last_date": commissioning_date,
            "km_at_last": 0,
            "inherited_from": "Puesta en Servicio",
        }
        logger.info(
            "Module %s: using commissioning_date %s as fallback for %s",
            module_id, commissioning_date, top_cycle,
        )

    # Apply hierarchy inheritance: higher cycles reset lower ones
    # For each cycle, check if a higher-hierarchy cycle has a MORE RECENT date
    for cycle_type in hierarchy:
        current = latest_by_cycle.get(cycle_type)
        current_date = current["last_date"] if current else None
        current_hierarchy = hierarchy[cycle_type]

        # Check all cycles with HIGHER hierarchy
        for other_cycle, other_hierarchy in hierarchy.items():
            if other_hierarchy <= current_hierarchy:
                continue  # Only check higher hierarchy cycles

            other = latest_by_cycle.get(other_cycle)
            if not other or not other["last_date"]:
                continue

            other_date = other["last_date"]

            # If higher cycle is more recent, it resets this cycle
            if current_date is None or other_date > current_date:
                latest_by_cycle[cycle_type] = {
                    "last_date": other_date,
                    "km_at_last": other["km_at_last"],
                    "inherited_from": other_cycle,
                }
                current_date = other_date  # Update for next comparison

    # Build key_data list using ALL cycles (needed for projection)
    # The template will filter to show only heavy cycles in the display table
    # NOTE: commissioning_date fallback for top_cycle is already applied above,
    # before inheritance, so it propagates correctly to lower cycles.
    
    for cycle_type, cycle_label, cycle_km in all_cycles:
        entry = latest_by_cycle.get(cycle_type, {})
        last_date = entry.get("last_date")
        km_at_last = entry.get("km_at_last")
        inherited_from = entry.get("inherited_from")

        if km_at_last is not None:
            km_since = max(0, km_total - km_at_last)
        else:
            km_since = None

        key_data.append(MaintenanceKeyData(
            cycle_type=cycle_type,
            cycle_label=cycle_label,
            cycle_km=cycle_km,
            last_date=last_date,
            km_at_last=km_at_last,
            km_since=km_since,
            inherited_from=inherited_from,
        ))

    logger.info(
        "Module %s: cycles found: %s | key_data entries: %d",
        module_id, list(latest_by_cycle.keys()), len(key_data),
    )

    return history, key_data
