"""
Stub data for fleet module cards.

This module provides mock data for the UI development phase.
Will be replaced by actual database queries in production.
"""

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal


@dataclass
class CoachInfo:
    """Information about a single coach in an EMU composition."""

    number: int  # Coach number (e.g., 5001, 4029)
    coach_type: str  # Type description (e.g., "MC1", "R1", "Motriz Cabecera")

    def __str__(self) -> str:
        return f"{self.coach_type} {self.number}"


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
    # Coach composition (optional, populated from Access)
    coaches: list[CoachInfo] = field(default_factory=list)
    # Reference date for RG/commissioning
    reference_date: date | None = None
    reference_type: str = ""  # "RG" or "Puesta en Servicio"

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


def generate_csr_modules() -> list[ModuleData]:
    """
    Generate stub data for 86 CSR modules.

    Rules:
    - M01-M42: cuadruplas (4 coaches)
    - M43-M86: triplas (3 coaches)
    """
    modules = []
    maintenance_types = ["IQ", "IB", "AN", "BA", "RS", "DA"]

    for i in range(1, 87):
        module_number = i
        module_id = f"M{module_number:02d}"

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
            )
        )

    return modules


def generate_toshiba_modules() -> list[ModuleData]:
    """
    Generate stub data for 25 Toshiba modules.

    Rules:
    - 13 triplas (3 coaches)
    - 12 cuadruplas (4 coaches)
    """
    modules = []
    maintenance_types = ["MEN", "RB", "RG"]

    # First 12 are cuadruplas, next 13 are triplas
    for i in range(1, 26):
        module_number = i
        module_id = f"T{module_number:02d}"

        if module_number <= 12:
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

    return {
        "csr_count": len(csr_modules),
        "toshiba_count": len(toshiba_modules),
        "total_count": len(modules),
        "csr_km_month": sum(m.km_current_month for m in csr_modules),
        "toshiba_km_month": sum(m.km_current_month for m in toshiba_modules),
        "total_km_month": sum(m.km_current_month for m in modules),
        "csr_km_total": sum(m.km_total_accumulated for m in csr_modules),
        "toshiba_km_total": sum(m.km_total_accumulated for m in toshiba_modules),
        "total_km_total": sum(m.km_total_accumulated for m in modules),
    }
