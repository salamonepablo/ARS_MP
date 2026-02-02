# Legacy Access Database Schema Overview

> **Generated:** 2026-02-02  
> **Tool:** `etl/extractors/access_introspect.py`

## Executive Summary

This document provides a technical overview of the legacy Microsoft Access databases used in the ARS_MP (Argentinian Rolling Stock Maintenance Planner) project. These databases contain historical maintenance data for the Roca Line railway fleet.

### Databases Analyzed

| Database | Format | Status | Tables | Columns |
|----------|--------|--------|--------|---------|
| DB_CCEE_Programación 1.1.accdb | Access 2007+ | **SUCCESS** | 57 | 453 |
| baseCCEE.mdb | Access 97/2000 | FAILED | - | - |
| baseCCRR.mdb | Access 97/2000 | FAILED | - | - |
| baseLocs.mdb | Access 97/2000 | FAILED | - | - |

### Key Findings

1. **Only the `.accdb` file is readable** with the current ACE ODBC driver (64-bit)
2. The `.mdb` files use Access 97/2000 format which requires conversion or the legacy Jet 4.0 driver (32-bit only)
3. The main database (`DB_CCEE_Programación 1.1.accdb`) contains comprehensive maintenance tracking data
4. **No foreign key relationships** were exposed by the ODBC driver (Access limitation)
5. Primary keys are inferred from unique indexes named "PrimaryKey"

---

## Database Purpose Analysis

### DB_CCEE_Programación 1.1.accdb

**Purpose:** Main operational database for CCEE (Centro de Control de Equipos Eléctricos) - tracks electric rolling stock maintenance for the Roca Line.

**Main functional areas:**

| Prefix | Area | Description |
|--------|------|-------------|
| `A_00_*` | Master Data | Vehicle classes, formations, modules, tasks, mileage |
| `A_01_*` | Materials | Material lists, replacements, issue types |
| `A_08_*` | Fleet Organs | Tracked components (parque de órganos) |
| `A_12_*` | Incidents | Accidental/unplanned maintenance events |
| `A_14_*` | Changes | Module and coach configuration changes |
| `A_15_*` | Washing | Formation washing records |
| `A_17_*` | Follow-ups | Units under special monitoring |
| `A_30_*` | Fire Extinguishers | Matafuegos tracking |
| `A_31_*` | Events | Event downloads/logging |
| `A_32_*` | Measurements | Lathe measurements (wheels) |
| `A_40_*` | Audits | Document auditing |
| `B_*` | Toshiba EMU | Maintenance specifics for Toshiba trains |
| `C_*` | CSR EMU | Maintenance specifics for CSR trains |

### baseCCEE.mdb, baseCCRR.mdb, baseLocs.mdb

**Purpose (inferred from filenames):**
- `baseCCEE.mdb`: Older CCEE data (electric stock)
- `baseCCRR.mdb`: CCRR data (possibly diesel railcars - Coches de Cercanías?)
- `baseLocs.mdb`: Locomotive data

**Status:** Cannot be read with current driver. Options:
1. Convert to `.accdb` format using MS Access
2. Use 32-bit Python with Jet 4.0 driver
3. Export to CSV/Excel manually

---

## Key Tables Analysis

### Master Data Tables

#### A_00_Módulos (Modules/Units)
```
Id_Módulos      COUNTER  PK
Módulos         VARCHAR  Unit identifier
Clase_Vehículos INTEGER  FK to vehicle class
Cabina          VARCHAR  Cabin designation
```
**Note:** This appears to be the main unit registry. A "módulo" typically represents a train consist.

#### A_00_Coches (Coaches/Cars)
```
Id_Coches       COUNTER  PK
Coche           INTEGER  Coach number
Ubicación       VARCHAR  Current location
Descripción     VARCHAR  Description
Clase_Vehículo  INTEGER  FK to vehicle class
Posición        VARCHAR  Position in consist
```

#### A_00_Kilometrajes (Mileage Readings)
```
Id_Kilometrajes COUNTER  PK
Módulo          INTEGER  FK to module
kilometraje     INTEGER  Odometer reading (km)
Fecha           DATETIME Reading date
```
**Critical for ETL:** This is the source for mileage projections.

#### A_00_Tareas (Maintenance Tasks)
```
Id_Tareas       COUNTER  PK
Ingreso         VARCHAR  Entry type
Tipo_Tarea      VARCHAR  Task type (preventive/corrective)
Tarea           VARCHAR  Task code/name
Descripción     VARCHAR  Task description
Clase_Vehículo  INTEGER  Applicable vehicle class
```

#### A_00_Próxima_Tarea (Next Task Rules)
```
Id_Próxima_Tarea    INTEGER
Tarea               VARCHAR  Current task
Próxima_Tarea       VARCHAR  Next scheduled task
Km_entre_Tareas     DOUBLE   Kilometers between tasks
Tiempo_entre_Tareas DOUBLE   Time between tasks
Km_resguardo        DOUBLE   Safety margin (km)
```
**Critical for ETL:** Defines maintenance cycle intervals.

### Maintenance Event Tables

#### A_00_OT_Simaf (Work Orders)
```
Id_OT_Simaf     COUNTER  PK
OT_Simaf        VARCHAR  UNIQUE - Work order number
Módulo          INTEGER  FK to module
Ingreso         VARCHAR  Entry type
Tipo_Tarea      VARCHAR  Task type
Tarea           VARCHAR  Task performed
Km              INTEGER  Mileage at intervention
Fecha_Inicio    DATETIME Start date
Fecha_Fin       DATETIME End date
```
**Note:** SIMAF appears to be the corporate maintenance management system.

#### B_02_Mantenimientos / C_02_Mantenimientos
Maintenance event records specific to Toshiba (B) and CSR (C) fleets.

### Fleet-Specific Tables

The database separates data by fleet type:
- **B_* tables:** Toshiba EMU (Electric Multiple Unit)
- **C_* tables:** CSR EMU

Both fleets have parallel structures for:
- Materials tracking (`B_01_Materiales`, `C_01_Materiales`)
- Issue logging (`B_01_Novedades`, `C_01_Novedades`)
- Maintenance events (`B_02_Mantenimientos`, `C_02_Mantenimientos`)
- Component measurements (brakes, pantograph, wheels, etc.)

---

## Data Quality Observations

### Naming Inconsistencies

| Issue | Examples |
|-------|----------|
| Mixed case | `kilometraje` vs `Km` vs `Kilometraje` |
| Accent variations | `Módulo` vs `Modulo` |
| Typos | `Sub_Gurpos` (should be Sub_Grupos) |
| Spanish/English mix | `Fecha_Inicio`, `Fecha_Fin` vs `Starts` |
| Column naming | `Ubición` (should be Ubicación) |

### Type Observations

| Pattern | Observation |
|---------|-------------|
| IDs | Mix of `COUNTER` (auto-increment) and `INTEGER` |
| Dates | All use `DATETIME` type |
| Large text | `LONGCHAR` for observations/comments (1GB max) |
| Booleans | `BIT` type with `NO` nullability |
| Numbers | Mix of `INTEGER`, `REAL`, `DOUBLE` |

### Potential Data Issues

1. **No enforced foreign keys** - referential integrity depends on application logic
2. **Inconsistent ID patterns** - some tables use `Id_TableName`, others use `Id` alone
3. **Denormalized data** - some tables store formatted strings instead of FK references
4. **Legacy GUID indexes** - several tables have indexes named like `{45675E34-AB47-49C3-...}` (Access internal)

---

## Saved Queries/Views

The database contains 7 saved queries:

| Query Name | Purpose (inferred) |
|------------|-------------------|
| `3_NUM_un_NSAP` | Unknown numbering query |
| `A_00_Kilometraje_Máx` | Maximum mileage per module |
| `A_14_Cambio_Coches_Último1` | Latest coach changes (variant 1) |
| `A_14_Cambio_Coches_Último2` | Latest coach changes (variant 2) |
| `A_14_Cambio_Módulos_Último1` | Latest module changes (variant 1) |
| `A_14_Cambio_Módulos_Último2` | Latest module changes (variant 2) |
| `A_14_Estado_Formaciones_Consulta` | Current formation status |

**Note:** Query SQL is not accessible via ODBC. Would need to open in MS Access to extract.

---

## ODBC Driver Limitations

The following metadata could NOT be extracted due to driver limitations:

| Feature | Status | Notes |
|---------|--------|-------|
| Tables | OK | All user tables retrieved |
| Columns | OK | Full metadata including types and sizes |
| Indexes | OK | Names, columns, uniqueness |
| **Foreign Keys** | FAILED | Driver returns empty results |
| **Query SQL** | FAILED | Only query names visible as VIEWs |
| **Check Constraints** | N/A | Not supported by Access |
| **Triggers** | N/A | Not supported by Access |

---

## Recommendations for ETL

### Priority Tables for Initial ETL

1. **A_00_Módulos** - Core unit registry
2. **A_00_Coches** - Coach inventory
3. **A_00_Kilometrajes** - Mileage history (critical for projections)
4. **A_00_Tareas** - Task definitions
5. **A_00_Próxima_Tarea** - Maintenance intervals
6. **A_00_OT_Simaf** - Work order history

### Data Transformation Needs

1. **Normalize mileage field names** → standardize to `kilometraje` or `km`
2. **Create explicit FK relationships** in PostgreSQL based on naming patterns
3. **Convert dates** with proper timezone handling
4. **Handle encoding** - source uses Windows-1252, target should be UTF-8
5. **Merge fleet-specific tables** where structure is identical (B_* and C_*)

### Handling Legacy .mdb Files

Options in order of preference:
1. **Convert to .accdb** using MS Access (preserves all data)
2. **Export to CSV** from MS Access (loses queries/macros)
3. **Use 32-bit Python** with Jet driver (complex setup)

---

## File Locations

```
docs/legacy_bd/
├── introspection/
│   ├── DB_CCEE_Programación 1.1/
│   │   ├── tables.csv
│   │   ├── columns.csv
│   │   ├── indexes.csv
│   │   ├── relationships.csv
│   │   ├── queries.csv
│   │   └── summary.md
│   ├── baseCCEE/
│   │   └── [error - empty files]
│   ├── baseCCRR/
│   │   └── [error - empty files]
│   └── baseLocs/
│       └── [error - empty files]
├── Accdb/
│   └── DB_CCEE_Programación 1.1.accdb
├── Access20/
│   ├── baseCCEE.mdb
│   ├── baseCCRR.mdb
│   └── baseLocs.mdb
└── access_schema_overview.md  (this file)
```
