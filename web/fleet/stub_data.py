"""
Stub data for fleet module cards.

This module provides mock data for the UI development phase.
Will be replaced by actual database queries in production.
"""

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

from core.domain.reference_data import RG_REFERENCE_DATES


@dataclass
class CoachInfo:
    """Information about a single coach in an EMU composition."""

    number: int  # Coach number (e.g., 5001, 4029)
    coach_type: str  # Type description (e.g., "MC1", "R1", "Motriz Cabecera")

    def __str__(self) -> str:
        return f"{self.coach_type} {self.number}"


@dataclass
class MaintenanceEvent:
    """A single maintenance event from the history."""

    event_date: date = field(default_factory=date.today)
    task_type: str = ""  # e.g., "IQ", "AN1", "RB", "RG"
    km_at_event: int = 0
    start_date: date | None = None
    end_date: date | None = None
    ot_simaf: str = ""
    duration_days: int | None = None


@dataclass
class MaintenanceKeyData:
    """Last intervention data for a specific maintenance cycle type.

    Used in the "Detalle Mantenimiento Pesado" section of the detail view.
    """

    cycle_type: str  # e.g., "AN", "BA", "PE", "DA", "RB", "RG"
    cycle_label: str  # Display name, e.g., "Anual (AN)", "Bienal (RB)"
    cycle_km: int  # Cycle interval in km (e.g., 187500 for AN)
    last_date: date | None = None
    km_at_last: int | None = None
    km_since: int | None = None  # km_total - km_at_last
    # If this cycle's data was inherited from a higher hierarchy cycle
    inherited_from: str | None = None  # e.g., "RG" if RB inherited from RG


@dataclass
class ModuleData:
    """Data structure for a fleet module card."""

    module_id: str
    module_number: int
    fleet_type: Literal["CSR", "Toshiba"]
    configuration: Literal["tripla", "cuadrupla"]
    coach_count: int
    km_current_month: int
    km_total_accumulated: int
    last_maintenance_date: date
    last_maintenance_type: str
    km_at_last_maintenance: int
    km_current_month_date: date | None = None
    # Internal Access DB FK (used to fetch detail data on demand)
    module_db_id: int | None = None
    # Coach composition (optional, populated from Access)
    coaches: list[CoachInfo] = field(default_factory=list)
    # Reference date for RG/commissioning
    reference_date: date | None = None
    reference_type: str = ""  # "RG" or "Puesta en Servicio"
    # Last RG (Revisión General) data - critical for Toshiba modules
    last_rg_date: date | None = None
    km_at_last_rg: int | None = None
    # Maintenance history (last year) for detail view
    maintenance_history: list[MaintenanceEvent] = field(default_factory=list)
    # Key data per maintenance cycle type for projection
    maintenance_key_data: list[MaintenanceKeyData] = field(default_factory=list)

    @property
    def km_since_maintenance(self) -> int:
        """Calculate km traveled since last maintenance."""
        return self.km_total_accumulated - self.km_at_last_maintenance

    @property
    def days_since_maintenance(self) -> int:
        """Calculate days since last maintenance."""
        return (date.today() - self.last_maintenance_date).days

    @property
    def coach_composition_str(self) -> str:
        """Return formatted coach composition string."""
        if not self.coaches:
            return ""
        return " - ".join(str(c) for c in self.coaches)

    @property
    def km_current_month_label(self) -> str:
        """Return Spanish month name for KM current month reference."""
        if not self.km_current_month_date:
            return ""
        return _get_month_name_es(self.km_current_month_date.month)

    @property
    def km_since_rg(self) -> int | None:
        """
        Calculate km traveled since last RG (Revisión General).
        
        This is the key metric for Toshiba heavy maintenance planning.
        RG cycle is every 600,000 km for Toshiba modules.
        
        Returns:
            KM since last RG, or None if no RG data available.
        """
        if self.km_at_last_rg is None:
            return None
        return self.km_total_accumulated - self.km_at_last_rg


def _get_month_name_es(month_number: int) -> str:
    """Return Spanish month name for a given month number (1-12)."""
    months = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    if 1 <= month_number <= 12:
        return months[month_number - 1]
    return ""


# =============================================================================
# Coach composition generation
# =============================================================================

# CSR coach number ranges by configuration
# Cuadruplas (4 coches): MC1 (5000s), R1 (4000s), R2 (4500s), MC2 (5500s)
# Triplas (3 coches): MC1 (5000s), R1 (4000s), MC2 (5500s)
CSR_COACH_BASES = {
    "cuadrupla": [("MC1", 5000), ("R1", 4000), ("R2", 4500), ("MC2", 5500)],
    "tripla": [("MC1", 5000), ("R1", 4000), ("MC2", 5500)],
}

# Toshiba coach number ranges
# Cuadruplas: M (2000s), R (2200s), R (2400s), M (2600s)
# Triplas: M (2000s), R (2200s), M (2600s)
TOSHIBA_COACH_BASES = {
    "cuadrupla": [("M", 2000), ("R", 2200), ("R", 2400), ("M", 2600)],
    "tripla": [("M", 2000), ("R", 2200), ("M", 2600)],
}


def _generate_coach_composition(
    module_number: int,
    fleet_type: Literal["CSR", "Toshiba"],
    configuration: Literal["tripla", "cuadrupla"],
) -> list[CoachInfo]:
    """Generate realistic coach composition for a module.

    Coach numbers are derived from the module number to maintain consistency.
    """
    if fleet_type == "CSR":
        bases = CSR_COACH_BASES[configuration]
    else:
        bases = TOSHIBA_COACH_BASES[configuration]

    coaches = []
    for coach_type, base_number in bases:
        # Generate coach number based on module number for consistency
        coach_number = base_number + module_number
        coaches.append(CoachInfo(number=coach_number, coach_type=coach_type))

    return coaches


# =============================================================================
# Maintenance cycle definitions
# =============================================================================

CSR_CYCLES = [
    ("AN", "Anual (AN)", 187_500),
    ("BA", "Bianual (BA)", 375_000),
    ("PE", "Pentanual (PE)", 750_000),
    ("DA", "Decanual (DA)", 1_500_000),
]

TOSHIBA_CYCLES = [
    ("RB", "Bienal (RB)", 300_000),
    ("RG", "Reparación General (RG)", 600_000),
]

# CSR maintenance task variants (Access stores AN1-AN6, BA1-BA3, etc.)
CSR_HISTORY_TASKS = ["IQ", "IQ", "IQ", "IB", "IB", "AN1", "AN2", "AN3", "BA1"]
TOSHIBA_HISTORY_TASKS = ["MEN", "MEN", "MEN", "MEN", "RB"]


def _generate_maintenance_history(
    fleet_type: str,
    km_total: int,
    base_date: date,
) -> list[MaintenanceEvent]:
    """Generate realistic maintenance history for the last 365 days."""
    history: list[MaintenanceEvent] = []
    tasks = CSR_HISTORY_TASKS if fleet_type == "CSR" else TOSHIBA_HISTORY_TASKS
    avg_daily_km = 392 if fleet_type == "CSR" else 260

    # Generate between 5-15 events spread over the last year
    num_events = random.randint(5, 15)
    for _ in range(num_events):
        days_ago = random.randint(1, 365)
        event_date = base_date - timedelta(days=days_ago)
        km_at_event = max(0, km_total - int(days_ago * avg_daily_km))
        task = random.choice(tasks)
        duration_days = random.randint(1, 3)
        start_date = event_date - timedelta(days=duration_days)
        ot_simaf = f"OT-{random.randint(1000, 9999)}"
        history.append(MaintenanceEvent(
            event_date=event_date,
            start_date=start_date,
            end_date=event_date,
            task_type=task,
            km_at_event=km_at_event,
            ot_simaf=ot_simaf,
            duration_days=duration_days,
        ))

    # Sort by date descending (most recent first)
    history.sort(key=lambda e: e.event_date, reverse=True)
    return history


def _generate_key_data_csr(
    km_total: int,
    reference_date: date | None,
) -> list[MaintenanceKeyData]:
    """Generate key maintenance data for CSR modules."""
    key_data: list[MaintenanceKeyData] = []
    today = date.today()

    for cycle_type, label, cycle_km in CSR_CYCLES:
        # Simulate that last intervention happened some fraction of cycle ago
        km_since = random.randint(int(cycle_km * 0.1), int(cycle_km * 0.85))
        km_at_last = km_total - km_since
        if km_at_last < 0:
            km_at_last = 0
            km_since = km_total
        # Estimate date based on ~392 km/day average
        days_ago = km_since // 392
        last_date = today - timedelta(days=days_ago)

        key_data.append(MaintenanceKeyData(
            cycle_type=cycle_type,
            cycle_label=label,
            cycle_km=cycle_km,
            last_date=last_date,
            km_at_last=km_at_last,
            km_since=km_since,
        ))

    # For DA: if no DA ever done, use reference_date (puesta en servicio)
    da_entry = key_data[-1]  # Last one is DA
    if reference_date and da_entry.km_since and da_entry.km_since > 1_200_000:
        # Probably never had a DA, use reference date as proxy
        da_entry.last_date = reference_date
        da_entry.km_at_last = 0
        da_entry.km_since = km_total

    return key_data


def _generate_key_data_toshiba(
    km_total: int,
    last_rg_date: date | None,
    km_at_last_rg: int | None,
) -> list[MaintenanceKeyData]:
    """Generate key maintenance data for Toshiba modules."""
    key_data: list[MaintenanceKeyData] = []
    today = date.today()

    for cycle_type, label, cycle_km in TOSHIBA_CYCLES:
        if cycle_type == "RG" and last_rg_date is not None and km_at_last_rg is not None:
            # Use real RG data that was already generated
            km_since = km_total - km_at_last_rg
            key_data.append(MaintenanceKeyData(
                cycle_type=cycle_type,
                cycle_label=label,
                cycle_km=cycle_km,
                last_date=last_rg_date,
                km_at_last=km_at_last_rg,
                km_since=max(0, km_since),
            ))
        else:
            # RB: simulate
            km_since = random.randint(int(cycle_km * 0.1), int(cycle_km * 0.85))
            km_at_last = km_total - km_since
            if km_at_last < 0:
                km_at_last = 0
                km_since = km_total
            days_ago = km_since // 260
            last_date = today - timedelta(days=days_ago)

            key_data.append(MaintenanceKeyData(
                cycle_type=cycle_type,
                cycle_label=label,
                cycle_km=cycle_km,
                last_date=last_date,
                km_at_last=km_at_last,
                km_since=km_since,
            ))

    return key_data


def generate_csr_modules() -> list[ModuleData]:
    """
    Generate stub data for 86 CSR modules.

    Rules:
    - M01-M42: cuadruplas (4 coaches)
    - M43-M86: triplas (3 coaches)
    - M67 excluded: never commissioned, used as parts donor
    """
    modules = []
    maintenance_types = ["IQ", "IB", "AN", "BA", "RS", "DA"]

    for i in range(1, 87):
        module_number = i
        module_id = f"M{module_number:02d}"

        # M67 excluded - never commissioned
        if module_number == 67:
            continue

        # Cuadruplas: 1-42, Triplas: 43-86
        if module_number <= 42:
            configuration = "cuadrupla"
            coach_count = 4
        else:
            configuration = "tripla"
            coach_count = 3

        # Generate realistic mock data
        km_total = random.randint(150_000, 1_200_000)
        km_month = random.randint(3_000, 15_000)
        days_ago = random.randint(5, 180)
        last_maint_date = date.today() - timedelta(days=days_ago)
        km_at_maint = km_total - random.randint(5_000, 50_000)

        # Get reference date from domain data
        ref_data = RG_REFERENCE_DATES.get(module_id)
        reference_date = ref_data[0] if ref_data else None
        reference_type = ref_data[1] if ref_data else ""

        # Generate coach composition
        coaches = _generate_coach_composition(module_number, "CSR", configuration)

        # Generate detail data
        history = _generate_maintenance_history("CSR", km_total, date.today())
        key_data = _generate_key_data_csr(km_total, reference_date)

        modules.append(
            ModuleData(
                module_id=module_id,
                module_number=module_number,
                fleet_type="CSR",
                configuration=configuration,
                coach_count=coach_count,
                km_current_month=km_month,
                km_total_accumulated=km_total,
                last_maintenance_date=last_maint_date,
                last_maintenance_type=random.choice(maintenance_types),
                km_at_last_maintenance=km_at_maint,
                km_current_month_date=date.today(),
                coaches=coaches,
                reference_date=reference_date,
                reference_type=reference_type,
                maintenance_history=history,
                maintenance_key_data=key_data,
            )
        )

    return modules


def generate_toshiba_modules() -> list[ModuleData]:
    """
    Generate stub data for 25 Toshiba modules.

    Uses actual Toshiba module IDs from reference_data (T04, T06, T09, etc.)
    with their real RG dates.

    Rules:
    - Cuadruplas: T04-T22 (even numbered, some gaps)
    - Triplas: T28-T52 (higher numbers)
    - RG cycle is every 600,000 km
    """
    modules = []
    maintenance_types = ["MEN", "RB", "RG"]

    # Get actual Toshiba module IDs from reference data
    toshiba_ids = sorted(
        [mid for mid in RG_REFERENCE_DATES.keys() if mid.startswith("T")],
        key=lambda x: int(x[1:])
    )

    # Cuadruplas: first 12 modules, Triplas: remaining 13
    cuadrupla_ids = toshiba_ids[:12]

    for module_id in toshiba_ids:
        module_number = int(module_id[1:])

        if module_id in cuadrupla_ids:
            configuration = "cuadrupla"
            coach_count = 4
        else:
            configuration = "tripla"
            coach_count = 3

        # Generate realistic mock data
        km_total = random.randint(200_000, 800_000)
        km_month = random.randint(4_000, 18_000)
        days_ago = random.randint(5, 120)
        last_maint_date = date.today() - timedelta(days=days_ago)
        km_at_maint = km_total - random.randint(8_000, 60_000)

        # Get real RG date from reference data
        ref_data = RG_REFERENCE_DATES.get(module_id)
        last_rg_date = ref_data[0] if ref_data else None
        reference_type = ref_data[1] if ref_data else "RG"

        # Calculate km at last RG based on date (estimate ~260 km/day average for Toshiba)
        if last_rg_date:
            days_since_rg = (date.today() - last_rg_date).days
            km_since_last_rg = min(int(days_since_rg * 260), km_total)
            km_at_last_rg = max(0, km_total - km_since_last_rg)
        else:
            km_since_last_rg = random.randint(50_000, 550_000)
            km_at_last_rg = max(0, km_total - km_since_last_rg)

        # Generate coach composition
        coaches = _generate_coach_composition(module_number, "Toshiba", configuration)

        # Generate detail data
        history = _generate_maintenance_history("Toshiba", km_total, date.today())
        key_data = _generate_key_data_toshiba(km_total, last_rg_date, km_at_last_rg)

        modules.append(
            ModuleData(
                module_id=module_id,
                module_number=module_number,
                fleet_type="Toshiba",
                configuration=configuration,
                coach_count=coach_count,
                km_current_month=km_month,
                km_total_accumulated=km_total,
                last_maintenance_date=last_maint_date,
                last_maintenance_type=random.choice(maintenance_types),
                km_at_last_maintenance=km_at_maint,
                km_current_month_date=date.today(),
                coaches=coaches,
                reference_date=last_rg_date,
                reference_type=reference_type,
                last_rg_date=last_rg_date,
                km_at_last_rg=km_at_last_rg,
                maintenance_history=history,
                maintenance_key_data=key_data,
            )
        )

    return modules


def get_all_modules() -> list[ModuleData]:
    """Get all modules (CSR + Toshiba) with consistent random seed."""
    random.seed(42)  # Consistent data across page loads
    csr = generate_csr_modules()
    toshiba = generate_toshiba_modules()
    return csr + toshiba


def get_fleet_summary(modules: list[ModuleData]) -> dict:
    """
    Calculate fleet summary KPIs.

    Returns:
        Dict with km totals for CSR, Toshiba, and combined.
    """
    csr_modules = [m for m in modules if m.fleet_type == "CSR"]
    toshiba_modules = [m for m in modules if m.fleet_type == "Toshiba"]

    month_label = ""
    for module in modules:
        if module.km_current_month_label:
            month_label = module.km_current_month_label
            break

    total_km_month = sum(m.km_current_month for m in modules)
    
    # Calculate average km per day (assuming 30-day month)
    avg_km_day = total_km_month // 30 if total_km_month > 0 else 0

    return {
        "csr_count": len(csr_modules),
        "toshiba_count": len(toshiba_modules),
        "total_count": len(modules),
        "csr_km_month": sum(m.km_current_month for m in csr_modules),
        "toshiba_km_month": sum(m.km_current_month for m in toshiba_modules),
        "total_km_month": total_km_month,
        "csr_km_total": sum(m.km_total_accumulated for m in csr_modules),
        "toshiba_km_total": sum(m.km_total_accumulated for m in toshiba_modules),
        "total_km_total": sum(m.km_total_accumulated for m in modules),
        "km_month_label": month_label,
        "avg_km_day": avg_km_day,
    }
