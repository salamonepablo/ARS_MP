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
        logger.info("Fetching coach composition from Access database...")
        cursor.execute(SQL_GET_COACH_COMPOSITION)
        
        for row in cursor.fetchall():
            module_db_id = row.Id_Módulos
            module_name = row.Módulos or ""
            coach_number = row.Coches
            description = row.Descripción
            
            # Determine fleet type from module name
            fleet_type = "CSR" if module_name.startswith("M") else "Toshiba"
            
            # Normalize coach type
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
    
    return ModuleData(
        module_id=module_id,
        module_number=module_number,
        fleet_type=fleet_type,
        configuration=configuration,
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
        
        # Get all modules
        logger.info("Fetching modules from Access database...")
        cursor.execute(SQL_GET_MODULES)
        module_rows = cursor.fetchall()
        
        # Get latest km per module (keyed by ModuloId which is the numeric FK)
        logger.info("Fetching kilometraje data...")
        cursor.execute(SQL_GET_LATEST_KM)
        km_data = {row.ModuloId: row for row in cursor.fetchall()}
        
        # Get km from 30 days ago for km_month calculation
        logger.info("Fetching previous month kilometraje data...")
        cursor.execute(SQL_GET_PREV_MONTH_KM)
        km_prev_data = {row.ModuloId: row for row in cursor.fetchall()}
        
        # Get last maintenance per module (keyed by ModuloId)
        logger.info("Fetching maintenance data...")
        cursor.execute(SQL_GET_LAST_MAINTENANCE)
        maint_data = {row.ModuloId: row for row in cursor.fetchall()}
        
        # Get coach composition per module
        logger.info("Fetching coach composition...")
        cursor.execute(SQL_GET_COACH_COMPOSITION)
        coaches_by_module: dict[int, list[CoachInfo]] = defaultdict(list)
        for coach_row in cursor.fetchall():
            module_db_id = coach_row.Id_Módulos
            module_name = coach_row.Módulos or ""
            coach_number = coach_row.Coches
            description = coach_row.Descripción
            
            # Determine fleet type from module name
            ft = "CSR" if module_name.startswith("M") else "Toshiba"
            coach_type = _normalize_coach_type(description, ft)
            
            coaches_by_module[module_db_id].append(
                CoachInfo(number=coach_number, coach_type=coach_type)
            )
        
        # Build ModuleData objects
        for row in module_rows:
            module_db_id = row.Id_Módulos
            module_name = row.Módulos
            
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
            km_row = km_data.get(module_db_id)
            km_total = km_row.kilometraje if km_row else 0
            
            # Calculate km_month as difference between current and 30 days ago
            km_prev_row = km_prev_data.get(module_db_id)
            if km_row and km_prev_row and km_total and km_prev_row.kilometraje:
                km_month = int(km_total) - int(km_prev_row.kilometraje)
                # Ensure non-negative (data quality issues may cause negative values)
                km_month = max(0, km_month)
            else:
                km_month = 0
            
            # Get maintenance data (lookup by module ID - FK relationship uses Id_Módulos)
            maint_row = maint_data.get(module_db_id)
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
