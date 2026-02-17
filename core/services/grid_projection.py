"""
Grid projection service for maintenance planning.

Generates an Excel-like grid that projects, month by month, the accumulated
km since last intervention for each heavy maintenance cycle of each module.

When the accumulated km exceeds the cycle threshold, the cell is flagged
as exceeded (triggers colour coding in the UI).

NO dependencies on Django or infrastructure layer.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date
from typing import Literal, Optional

from core.services.maintenance_projection import (
    CSR_HEAVY_CYCLES,
    TOSHIBA_HEAVY_CYCLES,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MONTHS: int = 18

DEFAULT_AVG_MONTHLY_KM: dict[str, int] = {
    "CSR": 12_000,
    "Toshiba": 8_000,
}

# Semaphore colour classes per cycle type (Tailwind CSS)
CYCLE_COLORS: dict[str, dict[str, str]] = {
    # CSR
    "AN": {"bg": "bg-green-100", "text": "text-green-800"},
    "BA": {"bg": "bg-yellow-100", "text": "text-yellow-800"},
    "PE": {"bg": "bg-sky-100", "text": "text-sky-800"},
    "DA": {"bg": "bg-red-100", "text": "text-red-800"},
    # Toshiba
    "RB": {"bg": "bg-yellow-100", "text": "text-yellow-800"},
    "RG": {"bg": "bg-red-100", "text": "text-red-800"},
}


# ---------------------------------------------------------------------------
# Data transfer objects
# ---------------------------------------------------------------------------

@dataclass
class MonthProjection:
    """Projection data for a single cell in the grid.

    Attributes:
        month_label: Human-readable month label (e.g. "Feb-26").
        km_accumulated: Projected accumulated km since last intervention.
        exceeded: True when km_accumulated >= cycle_km (threshold).
    """

    month_label: str
    km_accumulated: int
    exceeded: bool


@dataclass
class CycleRow:
    """One row in the grid: a maintenance cycle for a specific module.

    Attributes:
        cycle_type: Code of the cycle (e.g. "AN", "RB").
        cycle_label: Human-readable label.
        cycle_km: Cycle threshold in km.
        color_bg: Tailwind bg class for exceeded cells.
        color_text: Tailwind text class for exceeded cells.
        last_date: Date of the last intervention for this cycle (or None).
        months: List of MonthProjection, one per column.
    """

    cycle_type: str
    cycle_label: str
    cycle_km: int
    color_bg: str
    color_text: str
    last_date: date | None = None
    months: list[MonthProjection] = field(default_factory=list)


@dataclass
class ModuleGridData:
    """Grid data for a single module (groups several CycleRows).

    Attributes:
        module_id: Human-readable id (e.g. "M01", "T05").
        fleet_type: "CSR" or "Toshiba".
        cycle_rows: One CycleRow per heavy maintenance cycle.
    """

    module_id: str
    fleet_type: str
    cycle_rows: list[CycleRow] = field(default_factory=list)


@dataclass
class ModuleRankingEntry:
    """A single entry in the maintenance urgency ranking.

    Modules are ranked by km accumulated since their last RG or
    commissioning date, in descending order (most km = most urgent).

    Attributes:
        rank: 1-indexed position in the ranking.
        module_id: Human-readable id (e.g. "M01", "T05").
        fleet_type: "CSR" or "Toshiba".
        km_since_reference: Km accumulated since reference event.
        reference_date: Date of last RG or commissioning.
        reference_type: "RG" or "Puesta en Servicio".
    """

    rank: int
    module_id: str
    fleet_type: str
    km_since_reference: int
    reference_date: date | None
    reference_type: str


# ---------------------------------------------------------------------------
# Short month labels
# ---------------------------------------------------------------------------

_MONTH_ABBR = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _month_label(year: int, month: int) -> str:
    """Return a short label like 'Feb-26'."""
    return f"{_MONTH_ABBR[month]}-{year % 100:02d}"


# ---------------------------------------------------------------------------
# GridProjectionService
# ---------------------------------------------------------------------------

class GridProjectionService:
    """Pure business logic for the maintenance projection grid."""

    @staticmethod
    def project_cycle(
        km_since: int | None,
        cycle_km: int,
        avg_monthly_km: int,
        months: int = DEFAULT_MONTHS,
        reference_date: date | None = None,
    ) -> list[MonthProjection]:
        """Project accumulated km for a single cycle over N months.

        The current month is prorated: only the remaining days of the
        month contribute km.  Subsequent months add the full average.

        Args:
            km_since: Km accumulated since last intervention of this
                cycle type.  ``None`` is treated as 0.
            cycle_km: Cycle threshold (e.g. 187 500 for AN).
            avg_monthly_km: Average km per month for this fleet.
            months: How many months to project (default 18).
            reference_date: The "today" date.  Defaults to ``date.today()``.

        Returns:
            List of ``MonthProjection`` (length == *months*).
        """
        ref = reference_date or date.today()
        accumulated = km_since if km_since is not None else 0

        result: list[MonthProjection] = []

        year, month = ref.year, ref.month

        for i in range(months):
            days_in_month = calendar.monthrange(year, month)[1]

            if i == 0:
                # Current month: prorate by remaining days
                days_remaining = days_in_month - ref.day + 1
                km_add = int(avg_monthly_km / days_in_month * days_remaining)
            else:
                km_add = avg_monthly_km

            accumulated += km_add

            result.append(MonthProjection(
                month_label=_month_label(year, month),
                km_accumulated=accumulated,
                exceeded=accumulated >= cycle_km,
            ))

            # Advance to next month
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

        return result

    @staticmethod
    def project_module(
        module_id: str,
        fleet_type: Literal["CSR", "Toshiba"],
        key_data: list[dict],
        avg_monthly_km: int,
        months: int = DEFAULT_MONTHS,
        reference_date: date | None = None,
    ) -> ModuleGridData:
        """Project all heavy cycles for a single module.

        Args:
            module_id: e.g. "M01".
            fleet_type: "CSR" or "Toshiba".
            key_data: List of dicts with keys:
                - cycle_type (str)
                - cycle_km (int)
                - km_since (int | None)
                - last_date (date | None, optional)
            avg_monthly_km: Average km per month for this fleet.
            months: How many months to project.
            reference_date: "Today".

        Returns:
            ``ModuleGridData`` with one ``CycleRow`` per heavy cycle.
        """
        # Reversed: highest hierarchy first (DA, PE, BA, AN / RG, RB)
        heavy_cycles = list(reversed(
            CSR_HEAVY_CYCLES if fleet_type == "CSR"
            else TOSHIBA_HEAVY_CYCLES
        ))
        # Build lookup from key_data
        kd_lookup = {d["cycle_type"]: d for d in key_data}

        rows: list[CycleRow] = []
        for cycle_type, cycle_label, cycle_km in heavy_cycles:
            entry = kd_lookup.get(cycle_type, {})
            km_since = entry.get("km_since")
            last_date = entry.get("last_date")
            colors = CYCLE_COLORS.get(cycle_type, {"bg": "", "text": ""})

            projections = GridProjectionService.project_cycle(
                km_since=km_since,
                cycle_km=cycle_km,
                avg_monthly_km=avg_monthly_km,
                months=months,
                reference_date=reference_date,
            )

            rows.append(CycleRow(
                cycle_type=cycle_type,
                cycle_label=cycle_label,
                cycle_km=cycle_km,
                color_bg=colors["bg"],
                color_text=colors["text"],
                last_date=last_date,
                months=projections,
            ))

        return ModuleGridData(
            module_id=module_id,
            fleet_type=fleet_type,
            cycle_rows=rows,
        )

    @staticmethod
    def generate_grid(
        modules_data: list[dict],
        avg_monthly_km: int,
        months: int = DEFAULT_MONTHS,
        reference_date: date | None = None,
    ) -> list[ModuleGridData]:
        """Generate the full projection grid for a list of modules.

        Args:
            modules_data: List of dicts with keys:
                - module_id (str)
                - fleet_type (str)
                - key_data (list[dict])
            avg_monthly_km: Average km per month.
            months: Number of months to project.
            reference_date: "Today".

        Returns:
            List of ``ModuleGridData``, one per module.
        """
        result: list[ModuleGridData] = []
        ref = reference_date or date.today()

        for mod in modules_data:
            grid_data = GridProjectionService.project_module(
                module_id=mod["module_id"],
                fleet_type=mod["fleet_type"],
                key_data=mod.get("key_data", []),
                avg_monthly_km=avg_monthly_km,
                months=months,
                reference_date=ref,
            )
            result.append(grid_data)

        return result

    @staticmethod
    def rank_modules_by_urgency(
        modules_ranking_data: list[dict],
        top_n: int = 24,
    ) -> list[ModuleRankingEntry]:
        """Rank modules by maintenance urgency (most km since reference first).

        Modules are sorted by ``km_since_reference`` in descending order.
        Modules without km data (None) are placed last with km_since = 0.

        Args:
            modules_ranking_data: List of dicts with keys:
                - module_id (str)
                - fleet_type (str)
                - km_since_reference (int | None)
                - reference_date (date | None)
                - reference_type (str)
            top_n: Maximum number of modules to return (default 24).

        Returns:
            List of ``ModuleRankingEntry`` sorted by urgency, length
            <= *top_n*.
        """
        if not modules_ranking_data:
            return []

        # Normalise None km to 0 and sort descending
        def sort_key(m: dict) -> int:
            km = m.get("km_since_reference")
            return km if km is not None else 0

        sorted_modules = sorted(
            modules_ranking_data,
            key=sort_key,
            reverse=True,
        )

        result: list[ModuleRankingEntry] = []
        for i, mod in enumerate(sorted_modules[:top_n]):
            km = mod.get("km_since_reference")
            result.append(ModuleRankingEntry(
                rank=i + 1,
                module_id=mod["module_id"],
                fleet_type=mod["fleet_type"],
                km_since_reference=km if km is not None else 0,
                reference_date=mod.get("reference_date"),
                reference_type=mod.get("reference_type", ""),
            ))

        return result

    @staticmethod
    def get_month_headers(
        months: int = DEFAULT_MONTHS,
        reference_date: date | None = None,
    ) -> list[str]:
        """Return month header labels for the grid columns.

        Args:
            months: Number of months.
            reference_date: Start date.

        Returns:
            List of month labels (e.g. ["Feb-26", "Mar-26", ...]).
        """
        ref = reference_date or date.today()
        headers: list[str] = []
        year, month = ref.year, ref.month

        for _ in range(months):
            headers.append(_month_label(year, month))
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

        return headers
