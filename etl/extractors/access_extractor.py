"""
Access database data extractor for fleet modules.

Extracts module data from legacy Access database and converts
to ModuleData objects for the web interface.
"""

import csv
import logging
import os
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal, Optional

from web.fleet.stub_data import CoachInfo, ModuleData, get_all_modules

from .access_connection import (
    AccessConnectionError,
    get_access_connection,
    is_access_available,
)

logger = logging.getLogger(__name__)

DEFAULT_ACCESS_QUERY_TIMEOUT_SECONDS = 30


def _get_query_timeout_seconds() -> int:
    timeout_raw = os.environ.get("LEGACY_ACCESS_QUERY_TIMEOUT", "").strip()
    if not timeout_raw:
        return DEFAULT_ACCESS_QUERY_TIMEOUT_SECONDS

    try:
        timeout = int(timeout_raw)
    except ValueError:
        logger.warning(
            "Invalid LEGACY_ACCESS_QUERY_TIMEOUT value '%s'. Using default %s seconds.",
            timeout_raw,
            DEFAULT_ACCESS_QUERY_TIMEOUT_SECONDS,
        )
        return DEFAULT_ACCESS_QUERY_TIMEOUT_SECONDS

    if timeout <= 0:
        return 0

    return timeout


def _apply_query_timeout(cursor: Any, conn: Optional[Any] = None) -> None:
    timeout = _get_query_timeout_seconds()
    if timeout <= 0:
        return

    try:
        cursor.timeout = timeout
        return
    except Exception as e:
        logger.warning("Could not set cursor timeout (%s). Trying connection timeout.", e)

    if conn is None:
        return

    try:
        conn.timeout = timeout
    except Exception as e:
        logger.warning("Could not set connection timeout: %s", e)


# SQL Queries for data extraction
# Based on introspection of DB_CCEE_Programación 1.1.accdb

# Get all modules with their vehicle class
SQL_GET_MODULES = """
SELECT 
    m.Id_Módulos,
    m.Módulos,
    m.Clase_Vehículos,
    cv.Tipo_MR,
    cv.Marca_MR
FROM A_00_Módulos m
LEFT JOIN A_00_Clase_Vehículo cv ON m.Clase_Vehículos = cv.Id_Clase_Vehículo
ORDER BY m.Módulos
"""

# Get coach composition for each module from A_14_Estado_Formaciones_Consulta
# This query retrieves the list of coaches that form each EMU
# The Módulo field is the FK to A_00_Módulos.Id_Módulos
SQL_GET_COACH_COMPOSITION = """
SELECT 
    m.Id_Módulos,
    m.Módulos,
    f.Coches,
    f.[Descripción]
FROM A_14_Estado_Formaciones_Consulta f
INNER JOIN A_00_Módulos m ON f.[Módulo] = m.Id_Módulos
ORDER BY m.Módulos, f.Coches
"""

# Get ordered coach composition using A_00_Coches positions
SQL_GET_COACH_COMPOSITION_BY_POSITION = """
SELECT
    c.[Módulo] AS ModuloId,
    m.Módulos,
    c.Coche,
    c.[Posición] AS Posicion
FROM A_00_Coches AS c
INNER JOIN A_00_Módulos AS m ON c.[Módulo] = m.Id_Módulos
ORDER BY m.Módulos, c.[Posición]
"""

SQL_GET_COACH_COMPOSITION_BY_POSITION_NO_ACCENT = """
SELECT
    c.[Módulo] AS ModuloId,
    m.Módulos,
    c.Coche,
    c.Posicion
FROM A_00_Coches AS c
INNER JOIN A_00_Módulos AS m ON c.[Módulo] = m.Id_Módulos
ORDER BY m.Módulos, c.Posicion
"""

# Get latest kilometraje for each module
# Note: k.[Módulo] is a FK (numeric) to A_00_Módulos.Id_Módulos
# Access shows it as text via Lookup, but the actual value is the numeric ID
SQL_GET_LATEST_KM = """
SELECT
    k.[Módulo] AS ModuloId,
    k.kilometraje,
    k.Fecha
FROM A_00_Kilometrajes AS k
INNER JOIN (
    SELECT [Módulo], MAX(Fecha) AS MaxFecha
    FROM A_00_Kilometrajes
    GROUP BY [Módulo]
) AS latest ON k.[Módulo] = latest.[Módulo] AND k.Fecha = latest.MaxFecha
"""

# Get global max date for the kilometraje table
SQL_GET_GLOBAL_MAX_KM_DATE = """
SELECT MAX(Fecha) AS MaxFecha
FROM A_00_Kilometrajes
"""

# Get all kilometraje rows within a date range
SQL_GET_KM_RANGE = """
SELECT
    k.[Módulo] AS ModuloId,
    k.kilometraje,
    k.Fecha
FROM A_00_Kilometrajes AS k
WHERE k.Fecha >= ? AND k.Fecha <= ?
"""

# Get previous month kilometraje for km_month calculation
# This query gets the oldest reading within the last 30 days of available data
# Uses MAX(Fecha) from the table instead of Date() to handle historical data
SQL_GET_PREV_MONTH_KM = """
SELECT 
    k.[Módulo] AS ModuloId,
    k.kilometraje,
    k.Fecha
FROM A_00_Kilometrajes AS k
INNER JOIN (
    SELECT [Módulo], MIN(Fecha) AS MinFecha
    FROM A_00_Kilometrajes
    WHERE Fecha >= DateAdd('d', -30, (SELECT MAX(Fecha) FROM A_00_Kilometrajes))
    GROUP BY [Módulo]
) AS oldest ON k.[Módulo] = oldest.[Módulo] AND k.Fecha = oldest.MinFecha
"""

# Get previous kilometraje reading per module (regardless of date range)
# Use a per-module TOP 1 query to avoid heavy correlated subqueries
SQL_GET_PREV_KM_FOR_MODULE = """
SELECT TOP 1
    k.[Módulo] AS ModuloId,
    k.kilometraje,
    k.Fecha
FROM A_00_Kilometrajes AS k
WHERE k.[Módulo] = ? AND k.Fecha < ?
ORDER BY k.Fecha DESC
"""


# Get last maintenance event for each module
# Note: ot.[Módulo] is a FK (numeric) to A_00_Módulos.Id_Módulos
# Maintenance codes are in the 'Tarea' field (IQ, IB, AN1-6, BA1-3, RS, RG, MEN, RB, etc.)
SQL_GET_LAST_MAINTENANCE = """
SELECT 
    ot.[Módulo] AS ModuloId,
    ot.Tipo_Tarea,
    ot.Tarea,
    ot.Km,
    ot.Fecha_Fin
FROM A_00_OT_Simaf AS ot
INNER JOIN (
    SELECT [Módulo], MAX(Fecha_Fin) AS MaxFecha
    FROM A_00_OT_Simaf
    WHERE Tarea IN ('IQ', 'IQ1', 'IQ2', 'IQ3', 'IB', 'AN1', 'AN2', 'AN3', 'AN4', 'AN5', 'AN6', 
                    'BA1', 'BA2', 'BA3', 'RS', 'RG', 'MEN', 'RB')
    GROUP BY [Módulo]
) AS latest ON ot.[Módulo] = latest.[Módulo] AND ot.Fecha_Fin = latest.MaxFecha
"""

# Get last RG maintenance event for each module
SQL_GET_LAST_RG = """
SELECT
    ot.[Módulo] AS ModuloId,
    ot.Tipo_Tarea,
    ot.Tarea,
    ot.Km,
    ot.Fecha_Fin
FROM A_00_OT_Simaf AS ot
INNER JOIN (
    SELECT [Módulo], MAX(Fecha_Fin) AS MaxFecha
    FROM A_00_OT_Simaf
    WHERE Tarea = 'RG'
    GROUP BY [Módulo]
) AS latest ON ot.[Módulo] = latest.[Módulo] AND ot.Fecha_Fin = latest.MaxFecha
"""


# Path to URG-Modulos.csv (relative to project root)
URG_MODULOS_CSV_PATH = Path(__file__).parent.parent.parent / "docs" / "legacy_bd" / "Accdb" / "URG-Modulos.csv"


def _normalize_coach_type(description: Optional[str], fleet_type: str) -> str:
    """
    Normalize coach type description to standard abbreviation.
    
    Args:
        description: Raw description from Access (e.g., "Motriz Cabecera", "Remolque")
        fleet_type: "CSR" or "Toshiba"
        
    Returns:
        Standard abbreviation (MC1, MC2, R1, R2, M, R, RP)
    """
    if not description:
        return "?"
    
    desc = description.strip().lower()
    
    if fleet_type == "CSR":
        if "motriz cabecera" in desc or "cabecera" in desc:
            return "MC2"  # Motriz Cabecera
        if "cabina intermedia" in desc or "motriz" in desc:
            return "MC1"  # Motriz Cabina Intermedia  
        if "prima" in desc or "remolque prima" in desc:
            return "R2"  # Remolque Prima
        if "remolque" in desc:
            return "R1"  # Remolque
    else:  # Toshiba
        if "motriz" in desc or "cabecera" in desc:
            return "M"
        if "prima" in desc:
            return "RP"
        if "remolque" in desc:
            return "R"
    
    return "?"


def load_rg_dates_from_csv() -> dict[str, tuple[date, str]]:
    """
    Load RG/commissioning dates from URG-Modulos.csv.
    
    File format: Módulo;Manufacturer;Tipo;Fecha
    Example: MOD 01;CSR;Puesta en Servicio = Ultima RG;20/05/2015
    
    Returns:
        Dict mapping module_id (e.g., "M01", "T04") to (date, reference_type)
        where reference_type is "RG" or "Puesta en Servicio"
    """
    rg_dates: dict[str, tuple[date, str]] = {}
    
    if not URG_MODULOS_CSV_PATH.exists():
        logger.warning(f"URG-Modulos.csv not found at {URG_MODULOS_CSV_PATH}")
        return rg_dates
    
    try:
        with open(URG_MODULOS_CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                modulo_raw = row.get("Módulo", "").strip()
                manufacturer = row.get("Manufacturer", "").strip()
                tipo = row.get("Tipo", "").strip()
                fecha_str = row.get("Fecha", "").strip()
                
                if not modulo_raw or not fecha_str:
                    continue
                
                # Parse module number from "MOD 01" format
                match = re.search(r"\d+", modulo_raw)
                if not match:
                    continue
                module_num = int(match.group())
                
                # Determine prefix based on manufacturer
                if manufacturer.upper() == "CSR":
                    prefix = "M"
                elif manufacturer.upper() == "TOSHIBA":
                    prefix = "T"
                else:
                    continue
                
                module_id = f"{prefix}{module_num:02d}"
                
                # Parse date (format: DD/MM/YYYY)
                try:
                    reference_date = datetime.strptime(fecha_str, "%d/%m/%Y").date()
                except ValueError:
                    logger.warning(f"Could not parse date '{fecha_str}' for module {module_id}")
                    continue
                
                # Determine reference type
                if "puesta en servicio" in tipo.lower():
                    reference_type = "Puesta en Servicio"
                else:
                    reference_type = "RG"
                
                rg_dates[module_id] = (reference_date, reference_type)
        
        logger.info(f"Loaded {len(rg_dates)} RG dates from URG-Modulos.csv")
        
    except Exception as e:
        logger.error(f"Error reading URG-Modulos.csv: {e}")
    
    return rg_dates


def get_coach_composition_from_access() -> dict[int, list[CoachInfo]]:
    """
    Extract coach composition for each module from Access database.
    
    Returns:
        Dict mapping module_id (Id_Módulos) to list of CoachInfo
        
    Raises:
        AccessConnectionError: If connection fails
    """
    if not is_access_available():
        return {}
    
    conn = get_access_connection()
    coaches_by_module: dict[int, list[CoachInfo]] = defaultdict(list)
    
    try:
        cursor = conn.cursor()
        _apply_query_timeout(cursor, conn)
        logger.info("Fetching coach composition from Access database...")

        try:
            cursor.execute(SQL_GET_COACH_COMPOSITION_BY_POSITION)
            for row in cursor.fetchall():
                module_db_id = row.ModuloId
                module_name = getattr(row, "Módulos", "") or ""
                coach_number = getattr(row, "Coche", None) or getattr(row, "Coches", None)
                position = getattr(row, "Posicion", None) or getattr(row, "Posición", None)

                if coach_number is None or position is None:
                    continue

                fleet_type = "CSR" if module_name.startswith("M") else "Toshiba"
                coach_type = _coach_type_from_position(int(position), fleet_type)

                coaches_by_module[module_db_id].append(
                    CoachInfo(number=int(coach_number), coach_type=coach_type)
                )
        except Exception as e:
            logger.warning(f"Could not load ordered coach composition (accented): {e}.")
            try:
                cursor.execute(SQL_GET_COACH_COMPOSITION_BY_POSITION_NO_ACCENT)
                for row in cursor.fetchall():
                    module_db_id = row.ModuloId
                    module_name = getattr(row, "Módulos", "") or ""
                    coach_number = getattr(row, "Coche", None) or getattr(row, "Coches", None)
                    position = getattr(row, "Posicion", None) or getattr(row, "Posición", None)

                    if coach_number is None or position is None:
                        continue

                    fleet_type = "CSR" if module_name.startswith("M") else "Toshiba"
                    coach_type = _coach_type_from_position(int(position), fleet_type)

                    coaches_by_module[module_db_id].append(
                        CoachInfo(number=int(coach_number), coach_type=coach_type)
                    )
            except Exception as e_alt:
                logger.warning(
                    f"Could not load ordered coach composition (no accent): {e_alt}. Falling back."
                )
                cursor.execute(SQL_GET_COACH_COMPOSITION)
                for row in cursor.fetchall():
                    module_db_id = row.Id_Módulos
                    module_name = row.Módulos or ""
                    coach_number = row.Coches
                    description = row.Descripción

                    fleet_type = "CSR" if module_name.startswith("M") else "Toshiba"
                    coach_type = _normalize_coach_type(description, fleet_type)

                    coaches_by_module[module_db_id].append(
                        CoachInfo(number=coach_number, coach_type=coach_type)
                    )
        
        logger.info(f"Loaded coach composition for {len(coaches_by_module)} modules")
        return dict(coaches_by_module)
        
    except Exception as e:
        logger.warning(f"Could not load coach composition: {e}")
        return {}
    finally:
        conn.close()


def _parse_date(value: Any) -> Optional[date]:
    """Parse a date value from Access database."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def _normalize_module_id(value: Any) -> str:
    """Normalize module identifiers to zero-padded format (e.g., "M01")."""
    if value is None:
        return ""
    raw = str(value).strip().upper()
    if not raw:
        return ""

    match = re.search(r"([A-Z])\s*0*(\d+)", raw)
    if match:
        prefix = match.group(1)
        try:
            num = int(match.group(2))
        except ValueError:
            return raw
        return f"{prefix}{num:02d}"

    return raw


def _to_datetime(value: Any) -> Optional[datetime]:
    """Normalize Access date/time values to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    return None


def _get_prev_km_for_module(
    cursor: Any,
    module_db_id: int,
    latest_date: Optional[date],
) -> Optional[Any]:
    """
    Get the previous kilometraje reading for a module using a lightweight query.

    Args:
        cursor: Active database cursor
        module_db_id: Numeric module FK (A_00_Módulos.Id_Módulos)
        latest_date: Latest reading date for this module

    Returns:
        Row with ModuloId, kilometraje, Fecha, or None if not available
    """
    if not module_db_id or not latest_date:
        return None

    try:
        cursor.execute(SQL_GET_PREV_KM_FOR_MODULE, (module_db_id, latest_date))
        return cursor.fetchone()
    except Exception as e:
        logger.warning(
            f"Could not load previous kilometraje for module {module_db_id}: {e}"
        )
        return None


def _determine_fleet_type(tipo_mr: Optional[str], marca_mr: Optional[str], module_name: str) -> str:
    """
    Determine fleet type from vehicle class or module name.
    
    Args:
        tipo_mr: Type of rolling stock (e.g., "EMU")
        marca_mr: Brand (e.g., "CSR", "Toshiba")
        module_name: Module identifier (e.g., "M01", "T15")
        
    Returns:
        "CSR" or "Toshiba"
    """
    # First try marca
    if marca_mr:
        marca_upper = marca_mr.upper()
        if "CSR" in marca_upper:
            return "CSR"
        if "TOSHIBA" in marca_upper:
            return "Toshiba"
    
    # Fall back to module name pattern
    if module_name:
        name_upper = module_name.upper().strip()
        if name_upper.startswith("M"):
            return "CSR"
        if name_upper.startswith("T"):
            return "Toshiba"
    
    # Default to CSR if unknown
    logger.warning(f"Could not determine fleet type for module {module_name}, defaulting to CSR")
    return "CSR"


def _determine_configuration(module_name: str, fleet_type: str) -> tuple[str, int]:
    """
    Determine module configuration (tripla/cuadrupla) and coach count.
    
    Rules from business context:
    - CSR M01-M42: cuadrupla (4 coaches)
    - CSR M43-M86: tripla (3 coaches)
    - Toshiba: varies by module number (see docs)
    
    Args:
        module_name: Module identifier (e.g., "M01", "T15"). Required.
        fleet_type: "CSR" or "Toshiba"
        
    Returns:
        Tuple of (configuration, coach_count)
        
    Raises:
        ValueError: If module_name is empty or None
    """
    if not module_name:
        raise ValueError("module_name is required and cannot be empty")
    
    # Extract number from module name
    try:
        num_str = "".join(c for c in module_name if c.isdigit())
        module_num = int(num_str) if num_str else 0
    except ValueError:
        module_num = 0
    
    if fleet_type == "CSR":
        if module_num <= 42:
            return "cuadrupla", 4
        else:
            return "tripla", 3
    else:  # Toshiba
        # Toshiba cuadruplas: T06, T11, T12, T16, T20, T24, T29, T31, T34, T39, T45, T52
        toshiba_cuadruplas = {6, 11, 12, 16, 20, 24, 29, 31, 34, 39, 45, 52}
        if module_num in toshiba_cuadruplas:
            return "cuadrupla", 4
        else:
            return "tripla", 3


def _coach_type_from_position(position: int, fleet_type: str) -> str:
    """Map coach position to standard type code based on fleet rules."""
    csr_map = {1: "MC1", 2: "R1", 3: "R2", 4: "MC2"}
    toshiba_map = {1: "M", 2: "R", 3: "RP", 4: "M"}

    if fleet_type == "CSR":
        return csr_map.get(position, "?")
    return toshiba_map.get(position, "?")


def extract_module_data(
    row: Any,
    configuration: str,
    coach_count: int,
) -> ModuleData:
    """
    Convert a database row to a ModuleData object.
    
    Args:
        row: Row object with module data attributes
        configuration: "tripla" or "cuadrupla"
        coach_count: Number of coaches (3 or 4)
        
    Returns:
        ModuleData instance
    """
    # Extract module number from name
    module_name = str(row.module_name) if hasattr(row, 'module_name') else str(row.Módulos)
    num_str = "".join(c for c in module_name if c.isdigit())
    module_number = int(num_str) if num_str else 0
    
    # Normalize module ID format
    fleet_type = row.fleet_type if hasattr(row, 'fleet_type') else _determine_fleet_type(
        getattr(row, 'Tipo_MR', None),
        getattr(row, 'Marca_MR', None),
        module_name
    )
    
    prefix = "M" if fleet_type == "CSR" else "T"
    module_id = f"{prefix}{module_number:02d}"
    
    # Get kilometre values
    km_total = getattr(row, 'km_total', None) or getattr(row, 'kilometraje', 0) or 0
    km_month = getattr(row, 'km_month', None) or 0
    km_at_maint = getattr(row, 'km_at_maint', None) or getattr(row, 'Km', None) or 0
    
    # Get maintenance info
    last_maint_date = _parse_date(
        getattr(row, 'last_maint_date', None) or getattr(row, 'Fecha_Fin', None)
    )
    if last_maint_date is None:
        last_maint_date = date.today()
    
    last_maint_type = (
        getattr(row, 'last_maint_type', None) or 
        getattr(row, 'Tipo_Tarea', None) or 
        getattr(row, 'Tarea', None) or 
        "N/A"
    )
    
    fleet_type_literal: Literal["CSR", "Toshiba"] = "CSR" if fleet_type == "CSR" else "Toshiba"
    config_literal: Literal["tripla", "cuadrupla"] = "cuadrupla" if configuration == "cuadrupla" else "tripla"

    return ModuleData(
        module_id=module_id,
        module_number=module_number,
        fleet_type=fleet_type_literal,
        configuration=config_literal,
        coach_count=coach_count,
        km_current_month=int(km_month),
        km_total_accumulated=int(km_total),
        last_maintenance_date=last_maint_date,
        last_maintenance_type=str(last_maint_type),
        km_at_last_maintenance=int(km_at_maint),
    )


def get_modules_from_access() -> list[ModuleData]:
    """
    Extract all modules from the Access database.
    
    Queries the legacy database for:
    - Module list with vehicle class
    - Latest kilometraje readings
    - Last maintenance events
    - Coach composition for each EMU
    - RG/commissioning dates from CSV
    
    Returns:
        List of ModuleData objects
        
    Raises:
        AccessConnectionError: If connection fails
    """
    conn = get_access_connection()
    modules: list[ModuleData] = []
    
    # Load auxiliary data
    rg_dates = load_rg_dates_from_csv()
    
    try:
        cursor = conn.cursor()
        _apply_query_timeout(cursor, conn)
        
        # Get all modules
        logger.info("Fetching modules from Access database...")
        cursor.execute(SQL_GET_MODULES)
        module_rows = cursor.fetchall()
        
        # Map module DB id to module name for consistent lookups
        module_id_to_name = {
            row.Id_Módulos: _normalize_module_id(row.Módulos)
            for row in module_rows
            if getattr(row, "Módulos", None)
        }

        # Cache for previous km readings (fallback when month data is missing)
        km_prev_any_data: dict[str, Any] = {}

        # Global max date to define the month window
        logger.info("Fetching global kilometraje max date...")
        cursor.execute(SQL_GET_GLOBAL_MAX_KM_DATE)
        global_max_row = cursor.fetchone()
        global_max_dt = _to_datetime(global_max_row.MaxFecha) if global_max_row else None

        # Preload km readings for the global month window
        km_month_rows: list[Any] = []
        if global_max_dt:
            month_start = datetime(global_max_dt.year, global_max_dt.month, 1)
            logger.info("Fetching kilometraje for global month window...")
            cursor.execute(SQL_GET_KM_RANGE, (month_start, global_max_dt))
            km_month_rows = cursor.fetchall()

        km_month_min: dict[str, Any] = {}
        km_month_max: dict[str, Any] = {}
        for row in km_month_rows:
            module_raw = row.ModuloId
            module_key = _normalize_module_id(module_id_to_name.get(module_raw) or module_raw)
            if not module_key:
                continue

            row_date = _to_datetime(row.Fecha)
            row_km = row.kilometraje
            if row_km is None:
                continue

            if module_key not in km_month_min:
                km_month_min[module_key] = row
            else:
                min_row = km_month_min[module_key]
                min_date = _to_datetime(min_row.Fecha)
                if row_date and min_date:
                    if row_date < min_date or (row_date == min_date and row_km < min_row.kilometraje):
                        km_month_min[module_key] = row

            if module_key not in km_month_max:
                km_month_max[module_key] = row
            else:
                max_row = km_month_max[module_key]
                max_date = _to_datetime(max_row.Fecha)
                if row_date and max_date:
                    if row_date > max_date or (row_date == max_date and row_km > max_row.kilometraje):
                        km_month_max[module_key] = row

        
        # Get last maintenance per module (keyed by ModuloId)
        logger.info("Fetching maintenance data...")
        cursor.execute(SQL_GET_LAST_MAINTENANCE)
        maint_data = {row.ModuloId: row for row in cursor.fetchall()}

        # Get last RG maintenance per module (keyed by ModuloId)
        logger.info("Fetching RG maintenance data...")
        cursor.execute(SQL_GET_LAST_RG)
        rg_data = {row.ModuloId: row for row in cursor.fetchall()}
        
        # Get coach composition per module
        logger.info("Fetching coach composition...")
        coaches_by_module = get_coach_composition_from_access()
        
        # Get latest km per module (keyed by ModuloId which is the numeric FK)
        logger.info("Fetching latest kilometraje data...")
        cursor.execute(SQL_GET_LATEST_KM)
        latest_rows = cursor.fetchall()
        km_data: dict[str, Any] = {}
        for row in latest_rows:
            module_raw = row.ModuloId
            module_key = _normalize_module_id(module_id_to_name.get(module_raw) or module_raw)
            if not module_key:
                continue

            row_date = _to_datetime(row.Fecha)
            if module_key not in km_data:
                km_data[module_key] = row
                continue
            current = km_data[module_key]
            current_date = _to_datetime(current.Fecha)
            if row_date and current_date:
                if row_date > current_date or (row_date == current_date and row.kilometraje > current.kilometraje):
                    km_data[module_key] = row

        # Build ModuleData objects
        for row in module_rows:
            module_db_id = row.Id_Módulos
            module_name = _normalize_module_id(row.Módulos)
            
            # Skip rows without a valid module name
            if not module_name:
                logger.debug(f"Skipping module with id {module_db_id}: no name")
                continue
            
            # Skip placeholder modules (M00, T00 are not real fleet units)
            if module_name in ("M00", "T00"):
                logger.debug(f"Skipping placeholder module: {module_name}")
                continue
            
            # Determine fleet type and configuration
            fleet_type = _determine_fleet_type(row.Tipo_MR, row.Marca_MR, module_name)
            configuration, coach_count = _determine_configuration(module_name, fleet_type)
            
            # Get km data (lookup by module ID - FK relationship uses Id_Módulos)
            module_key = _normalize_module_id(module_name)
            km_row = km_data.get(module_key)
            km_total = km_row.kilometraje if km_row else 0
            km_current_month_date = global_max_dt.date() if global_max_dt else _parse_date(km_row.Fecha) if km_row else None

            # Calculate km_month as difference between max and min in global month window
            month_min_row = km_month_min.get(module_key)
            month_max_row = km_month_max.get(module_key)
            if month_min_row and month_max_row:
                min_km = month_min_row.kilometraje
                max_km = month_max_row.kilometraje
                if min_km is not None and max_km is not None:
                    km_month = int(max_km) - int(min_km)
                    km_month = max(0, km_month)
                else:
                    km_month = 0
            else:
                # Fallback: use previous reading (any previous)
                km_prev_row = None
                if km_row:
                    if module_key not in km_prev_any_data:
                        km_prev_any_data[module_key] = _get_prev_km_for_module(
                            cursor,
                            module_db_id,
                            _parse_date(km_row.Fecha),
                        )
                    km_prev_row = km_prev_any_data.get(module_key)

                if km_row and km_prev_row and km_total and km_prev_row.kilometraje:
                    prev_km = km_prev_row.kilometraje
                    if prev_km is not None:
                        km_month = int(km_total) - int(prev_km)
                        km_month = max(0, km_month)
                    else:
                        km_month = 0
                else:
                    km_month = 0
            
            # Get maintenance data (lookup by module ID - FK relationship uses Id_Módulos)
            maint_row = maint_data.get(module_db_id)
            rg_row = rg_data.get(module_db_id)

            if fleet_type == "Toshiba" and rg_row:
                last_maint_date = _parse_date(rg_row.Fecha_Fin) if rg_row else date.today()
                last_maint_type = "RG"
                km_at_maint = rg_row.Km if rg_row else 0
            else:
                last_maint_date = _parse_date(maint_row.Fecha_Fin) if maint_row else date.today()
                last_maint_type = maint_row.Tarea if maint_row else "N/A"  # Tarea has the maintenance code (IQ, IB, AN, etc.)
                km_at_maint = maint_row.Km if maint_row else 0
            
            # Get coach composition
            coaches = coaches_by_module.get(module_db_id, [])
            
            # Create module ID
            num_str = "".join(c for c in module_name if c.isdigit())
            module_number = int(num_str) if num_str else 0
            prefix = "M" if fleet_type == "CSR" else "T"
            module_id = f"{prefix}{module_number:02d}"
            
            # Get RG date from CSV
            reference_date = None
            reference_type = ""
            if module_id in rg_dates:
                reference_date, reference_type = rg_dates[module_id]
            
            # Cast to Literal types for type safety
            fleet_type_literal: Literal["CSR", "Toshiba"] = "CSR" if fleet_type == "CSR" else "Toshiba"
            config_literal: Literal["tripla", "cuadrupla"] = "cuadrupla" if configuration == "cuadrupla" else "tripla"
            
            modules.append(ModuleData(
                module_id=module_id,
                module_number=module_number,
                fleet_type=fleet_type_literal,
                configuration=config_literal,
                coach_count=coach_count,
                km_current_month=km_month,
                km_total_accumulated=km_total or 0,
                last_maintenance_date=last_maint_date or date.today(),
                last_maintenance_type=str(last_maint_type),
                km_at_last_maintenance=km_at_maint or 0,
                coaches=coaches,
                reference_date=reference_date,
                reference_type=reference_type,
                km_current_month_date=km_current_month_date,
            ))
        
        logger.info(f"Extracted {len(modules)} modules from Access database")
        return modules
        
    finally:
        conn.close()


def get_modules_with_fallback() -> list[ModuleData]:
    """
    Get modules from Access database, falling back to stub data if unavailable.
    
    This is the main entry point for the web views. It provides graceful
    degradation when the Access database is not available (e.g., in CI,
    development without database, missing driver).
    
    Returns:
        List of ModuleData objects (from Access or stub data)
    """
    if not is_access_available():
        logger.warning(
            "Access database not available. Using stub data as fallback. "
            "Set LEGACY_ACCESS_DB_PATH and LEGACY_ACCESS_DB_PASSWORD in .env "
            "to connect to the real database."
        )
        return get_all_modules()
    
    try:
        return get_modules_from_access()
    except AccessConnectionError as e:
        logger.warning(f"Failed to connect to Access database: {e}. Using stub data.")
        return get_all_modules()
    except Exception as e:
        logger.error(f"Unexpected error extracting from Access: {e}. Using stub data.")
        return get_all_modules()
