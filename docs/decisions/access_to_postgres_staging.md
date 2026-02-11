# Access to Postgres staging — Decision Record

Date: 2026-02-10 (proposal) → 2026-02-11 (implemented)
Status: **Implemented**

---

## Context

The initial ARS_MP prototype reads fleet data **directly from the legacy Access
database** (.accdb) through ODBC on every HTTP request.  This path is:

1. **Fragile** — Access ODBC has quirks: no cursor timeout support, lookup
   fields that silently resolve to numeric FKs, `Nz()` not available over ODBC,
   parenthesised JOINs required, and encoding warnings on column names with
   accented characters (e.g. `Módulos`, `Vehículos`).

2. **Slow** — Each page load opens a new ODBC connection to the `.accdb` file,
   runs 5-8 SQL queries (modules, km, maintenance, coaches, RG), and closes.
   The list view takes ~3-4 seconds; the detail view adds another ~1-2 seconds
   for per-module history queries.

3. **Hard to test** — Unit tests can't easily mock an Access ODBC connection.
   CI environments don't have the Access ODBC driver at all.

4. **Blocking future features** — Projection grids, aggregated dashboards, and
   materialized views require SQL capabilities that Access doesn't offer (window
   functions, CTEs, proper date arithmetic, indexes on expressions).

## Decision

Introduce a **staging layer** in PostgreSQL that mirrors the 5 core Access
tables.  All business logic and web views read from Postgres.  Access is only
used as a **source system**, synced periodically via a management command.

### Why this approach (and not alternatives)

| Alternative | Why discarded |
|---|---|
| Keep reading from Access | Fragile, slow, untestable — the problems above. |
| Import into Django domain models directly | The domain models (`EmuModel`, `CoachModel`) have richer schema and constraints.  Mapping raw Access data directly into them would mix ETL concerns with domain logic and make incremental sync harder.  Staging tables are intentionally loose (nullable, no FKs) to absorb messy legacy data. |
| Use SQLAlchemy + Access engine | Still ODBC-dependent at request time; adds a second ORM to the project. |
| ETL to CSV/Parquet intermediate | Adds file I/O complexity; Postgres is already running and gives us SQL for free. |

### Architecture

```
┌──────────────┐   sync_access   ┌──────────────┐   Django ORM   ┌──────────────┐
│ Access .accdb │ ──────────────► │  Postgres    │ ◄──────────── │  Web Views   │
│  (ODBC, r/o)  │   (management   │  stg_* tables │   (read-only)  │  (list/detail)│
└──────────────┘    command)      └──────────────┘               └──────────────┘
```

The fallback chain in `get_modules_with_fallback()` is now:

1. **Postgres staging** (preferred) — if `stg_modulo` has rows.
2. **Live ODBC to Access** — if staging is empty but Access is configured.
3. **Stub data** — development/CI fallback.

## Implementation details

### Staging tables (migration `0002_staging_raw_tables`)

| Django model | Postgres table | Access source | Rows (Feb 2026) | Sync strategy |
|---|---|---|---|---|
| `StgModulo` | `stg_modulo` | `A_00_Módulos` + `A_00_Clase_Vehículo` | 114 | Full replace |
| `StgKilometraje` | `stg_kilometraje` | `A_00_Kilometrajes` | 191,182 | Full or incremental (by `fecha`) |
| `StgOtSimaf` | `stg_ot_simaf` | `A_00_OT_Simaf` | 28,674 | Full or incremental (by `fecha_fin` + hash dedup) |
| `StgCoche` | `stg_coche` | `A_00_Coches` | 392 | Full replace |
| `StgFormacionModulo` | `stg_formacion_modulo` | `A_14_Estado_Formaciones_Consulta` | 388 | Full replace |

### Management command: `sync_access`

```bash
# Full reload (default) — ~34 seconds for all 220K+ rows
python manage.py sync_access

# Specific tables only
python manage.py sync_access --tables modulos coches

# Incremental (km and OTs only — others always full replace)
python manage.py sync_access --incremental

# Dry run — read from Access, report counts, don't write
python manage.py sync_access --dry-run
```

Location: `infrastructure/database/management/commands/sync_access.py`

### Postgres extractor: `postgres_extractor.py`

Location: `etl/extractors/postgres_extractor.py`

Two public functions that mirror the Access extractor API:

- `get_modules_from_postgres() -> list[ModuleData]` — builds the full module
  list (used by the list view).  Reads from all 5 staging tables using Django
  ORM aggregations (`Max`, `Min`, `annotate`).

- `get_module_detail_from_postgres(...) -> tuple[list[MaintenanceEvent], list[MaintenanceKeyData]]`
  — loads maintenance history (last 365 days) and key cycle data for a specific
  module (used by the detail view).

- `is_postgres_staging_available() -> bool` — checks if `stg_modulo` has rows.

### View changes

- `get_modules_with_fallback()` (in `access_extractor.py`) now implements the
  3-tier fallback: Postgres → Access ODBC → Stub.

- `module_detail` view (in `web/fleet/views.py`) calls
  `get_module_detail_from_postgres()` when staging is available, otherwise
  falls back to `get_module_detail_from_access()`.

- The `data_source` badge in the detail template now shows `POSTGRES`, `ACCESS`,
  or `STUB` depending on which tier served the data.

### Data quality note

Access has ~1,062 duplicate rows in `A_00_Kilometrajes` (same `[Módulo]` +
`Fecha`).  The `sync_access` command deduplicates in memory, keeping the
highest `kilometraje` value for each `(modulo, fecha)` pair.

## Risks / Costs

- **Data freshness** — Views show data as of the last `sync_access` run.
  For the current use case (daily planning), running sync 1-3 times per day
  is sufficient.  Scheduling can be done via Windows Task Scheduler or cron.

- **Operational complexity** — One extra step (`sync_access`) before the app
  shows current data.  Mitigated by the Tier 2 fallback (live ODBC still works
  if staging is empty).

- **Schema drift** — If Access tables change, the staging models and sync
  queries need updating.  This is manageable since the Access schema hasn't
  changed since 2015.

## Open questions (resolved)

| Question | Resolution |
|---|---|
| Best incremental key per table | `fecha` for km, `fecha_fin` + `access_row_hash` for OTs.  Módulos/coches/formaciones always full replace (small tables). |
| Sync frequency | 1-3 times/day via scheduled task.  Manual `sync_access` for ad-hoc refreshes. |
| ETL scheduling ownership | Django management command (`sync_access`), invokable from cron/Task Scheduler. |

## Files created / modified

| File | Change |
|---|---|
| `infrastructure/database/models.py` | Added 5 `Stg*` staging models |
| `infrastructure/database/migrations/0002_staging_raw_tables.py` | Migration for staging tables |
| `infrastructure/database/management/commands/sync_access.py` | **New** — management command |
| `etl/extractors/postgres_extractor.py` | **New** — reads from staging tables |
| `etl/extractors/access_extractor.py` | Modified `get_modules_with_fallback()` → 3-tier fallback |
| `web/fleet/views.py` | Detail view prefers Postgres; badge shows data source |
| `docs/decisions/access_to_postgres_staging.md` | This document (updated) |
