"""
Maintenance projection and history services.

Pure business logic for calculating next maintenance interventions
and extracting key data per maintenance cycle type.

NO dependencies on Django or infrastructure layer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal


# ---------------------------------------------------------------------------
# Constants: maintenance cycle definitions
# ---------------------------------------------------------------------------

CSR_MAINTENANCE_CYCLES: list[tuple[str, str, int]] = [
    ("AN", "Anual (AN)", 187_500),
    ("BA", "Bianual (BA)", 375_000),
    ("PE", "Pentanual (PE)", 750_000),
    ("DA", "Decanual (DA)", 1_500_000),
]

TOSHIBA_MAINTENANCE_CYCLES: list[tuple[str, str, int]] = [
    ("RB", "Bienal (RB)", 300_000),
    ("RG", "Reparación General (RG)", 600_000),
]

# Average daily km by fleet (from business spec)
AVG_DAILY_KM: dict[str, int] = {
    "CSR": 392,       # ~12.000 km/month
    "Toshiba": 260,   # ~7.800 km/month
}

# Access DB task codes that map to each cycle type
# AN1-AN6 are subtypes of AN, BA1-BA3 of BA, etc.
TASK_TO_CYCLE: dict[str, str] = {
    "AN1": "AN", "AN2": "AN", "AN3": "AN",
    "AN4": "AN", "AN5": "AN", "AN6": "AN", "AN": "AN",
    "BA1": "BA", "BA2": "BA", "BA3": "BA", "BA": "BA",
    "RS": "PE", "PE": "PE",
    "DA": "DA", "RG": "RG", "RE": "DA",
    "RB": "RB",
    "MEN": "MEN",
    "IQ": "IQ", "IQ1": "IQ", "IQ2": "IQ", "IQ3": "IQ",
    "IB": "IB",
}


# ---------------------------------------------------------------------------
# Data transfer objects
# ---------------------------------------------------------------------------

@dataclass
class ProjectionResult:
    """Result of a maintenance projection calculation.

    Attributes:
        cycle_type: Code of the projected intervention (e.g. "AN", "RB").
        cycle_label: Human-readable label.
        cycle_km: Cycle interval in km.
        km_remaining: Km until next intervention.
        estimated_date: Projected date of next intervention.
        km_since_last: Km since the last intervention of this type.
        last_date: Date of last intervention of this type.
    """

    cycle_type: str
    cycle_label: str
    cycle_km: int
    km_remaining: int
    estimated_date: date
    km_since_last: int
    last_date: date | None


# ---------------------------------------------------------------------------
# MaintenanceProjectionService
# ---------------------------------------------------------------------------

class MaintenanceProjectionService:
    """Calculate projected next maintenance intervention.

    Determines which cycle will expire first based on km traveled
    since the last intervention of each type, and estimates the date
    using the fleet average daily km.
    """

    @staticmethod
    def get_cycles_for_fleet(
        fleet_type: Literal["CSR", "Toshiba"],
    ) -> list[tuple[str, str, int]]:
        """Return maintenance cycle definitions for a fleet type."""
        if fleet_type == "CSR":
            return CSR_MAINTENANCE_CYCLES
        return TOSHIBA_MAINTENANCE_CYCLES

    @staticmethod
    def project_next_intervention(
        fleet_type: Literal["CSR", "Toshiba"],
        km_total: int,
        key_data: list[dict],
        avg_daily_km: int | None = None,
        reference_date: date | None = None,
    ) -> ProjectionResult | None:
        """Calculate the next maintenance intervention.

        Args:
            fleet_type: "CSR" or "Toshiba".
            km_total: Current total accumulated km.
            key_data: List of dicts with keys:
                - cycle_type (str)
                - cycle_km (int)
                - km_at_last (int | None)
                - last_date (date | None)
            avg_daily_km: Override for average daily km. If None, uses
                fleet default.
            reference_date: Date to calculate from. Defaults to today.

        Returns:
            ProjectionResult for the cycle that expires soonest,
            or None if no data available.
        """
        if not key_data:
            return None

        daily_km = avg_daily_km or AVG_DAILY_KM.get(fleet_type, 392)
        ref_date = reference_date or date.today()

        cycles = MaintenanceProjectionService.get_cycles_for_fleet(fleet_type)
        cycle_lookup = {c[0]: (c[1], c[2]) for c in cycles}

        best: ProjectionResult | None = None

        for entry in key_data:
            ctype = entry.get("cycle_type", "")
            cycle_km = entry.get("cycle_km", 0)
            km_at_last = entry.get("km_at_last")
            last_date = entry.get("last_date")

            if not ctype or not cycle_km:
                continue

            label, _ = cycle_lookup.get(ctype, (ctype, cycle_km))

            # Calculate km since last intervention of this type
            if km_at_last is not None:
                km_since = km_total - km_at_last
            else:
                km_since = km_total  # Never done, count from zero

            km_remaining = max(0, cycle_km - km_since)

            # Estimate date
            if daily_km > 0 and km_remaining > 0:
                days_remaining = math.ceil(km_remaining / daily_km)
            else:
                days_remaining = 0
            estimated = ref_date + timedelta(days=days_remaining)

            candidate = ProjectionResult(
                cycle_type=ctype,
                cycle_label=label,
                cycle_km=cycle_km,
                km_remaining=km_remaining,
                estimated_date=estimated,
                km_since_last=km_since,
                last_date=last_date,
            )

            # Pick the one that expires soonest (smallest km_remaining)
            if best is None or km_remaining < best.km_remaining:
                best = candidate

        return best


# ---------------------------------------------------------------------------
# MaintenanceHistoryService
# ---------------------------------------------------------------------------

class MaintenanceHistoryService:
    """Extract and organize maintenance history data.

    Provides the 'datos clave' section and history filtering.
    Pure functions - no side effects.
    """

    @staticmethod
    def get_last_intervention_per_cycle(
        fleet_type: Literal["CSR", "Toshiba"],
        history: list[dict],
        km_total: int,
    ) -> list[dict]:
        """Extract the last intervention for each maintenance cycle type.

        Args:
            fleet_type: "CSR" or "Toshiba".
            history: List of dicts with keys:
                - task_type (str)
                - event_date (date)
                - km_at_event (int)
            km_total: Current total accumulated km.

        Returns:
            List of dicts with keys:
                - cycle_type, cycle_label, cycle_km
                - last_date, km_at_last, km_since
            One entry per cycle type, ordered by cycle_km ascending.
        """
        if fleet_type == "CSR":
            cycles = CSR_MAINTENANCE_CYCLES
        else:
            cycles = TOSHIBA_MAINTENANCE_CYCLES

        # Find latest event for each cycle type
        latest_by_cycle: dict[str, dict] = {}
        for event in history:
            task = event.get("task_type", "")
            cycle = TASK_TO_CYCLE.get(task)
            if cycle is None:
                continue

            event_date = event.get("event_date")
            km_at = event.get("km_at_event", 0)

            if cycle not in latest_by_cycle:
                latest_by_cycle[cycle] = {
                    "last_date": event_date,
                    "km_at_last": km_at,
                }
            else:
                existing = latest_by_cycle[cycle]
                if event_date and existing["last_date"] and event_date > existing["last_date"]:
                    latest_by_cycle[cycle] = {
                        "last_date": event_date,
                        "km_at_last": km_at,
                    }

        result = []
        for cycle_type, cycle_label, cycle_km in cycles:
            entry = latest_by_cycle.get(cycle_type, {})
            km_at_last = entry.get("km_at_last")
            km_since = (km_total - km_at_last) if km_at_last is not None else None

            result.append({
                "cycle_type": cycle_type,
                "cycle_label": cycle_label,
                "cycle_km": cycle_km,
                "last_date": entry.get("last_date"),
                "km_at_last": km_at_last,
                "km_since": km_since,
            })

        return result

    @staticmethod
    def filter_history_last_year(
        history: list[dict],
        reference_date: date | None = None,
    ) -> list[dict]:
        """Filter maintenance events to the last 365 days.

        Args:
            history: List of event dicts with 'event_date' key.
            reference_date: Date to count back from. Defaults to today.

        Returns:
            Filtered list, sorted by event_date descending.
        """
        ref = reference_date or date.today()
        cutoff = ref - timedelta(days=365)

        filtered = [
            e for e in history
            if e.get("event_date") and e["event_date"] >= cutoff
        ]
        filtered.sort(key=lambda e: e["event_date"], reverse=True)
        return filtered
