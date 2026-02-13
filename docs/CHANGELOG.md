# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-02-12

First feature-complete release for the TFM (Trabajo Final de Master).

### Added

- **Fleet module list** (`/fleet/modules/`):
  - 111 module cards (86 CSR + 25 Toshiba) with monthly km, total km, last maintenance info
  - Fleet filter (all / CSR / Toshiba)

- **Module detail view** (`/fleet/modules/<id>/`):
  - General info, kilometrage, coach composition
  - Heavy maintenance table with progress bars per cycle
  - Maintenance history (last year)
  - Quick module selector dropdown

- **Maintenance Projection Grid** (`/fleet/planner/`):
  - Excel-like grid projecting km per heavy cycle per module, month by month (default 18)
  - Fleet selector (CSR/Toshiba), configurable months and avg km/month
  - Colour-coded semaphore: green (AN), yellow (BA/RB), sky-blue (PE), red (DA/RG)
  - Double-click to mark interventions with hierarchy reset (Alpine.js)
  - Prorated current month based on day of month
  - Sticky columns (Module, Date, Cycle, Threshold) for horizontal scrolling
  - Summary footer: one row per heavy cycle + "Control" total row
  - Fecha column showing last maintenance date per cycle row

- **Excel export** (`/fleet/planner/export/`):
  - openpyxl-generated .xlsx with matching colour fills
  - Intervention-aware export: parses client-side interventions, applies text + colors
  - Recalculates km from 0 for intervened rows and heir rows
  - Summary rows and Control footer
  - Freeze panes, European number format, date format DD/MM/YYYY

- **ETL Pipeline**:
  - Access ODBC connection manager (read-only, with fallback)
  - Access data extractor with query timeout and BOM-safe CSV support
  - PostgreSQL staging tables (`StgModulo`, `StgKilometraje`, `StgMantenimiento`)
  - `sync_access` management command with incremental updates and SyncLog
  - `postgres_extractor` for querying staging tables from web views
  - Graceful fallback to stub data (111 modules) when Access unavailable

- **Maintenance hierarchy engine**:
  - CSR: DA > PE > BA > AN > IB > IQ (6 cycles, 4 heavy)
  - Toshiba: RG > RB > MEN (3 cycles, 2 heavy)
  - Higher interventions reset lower ones (`inherited_from` tracking)
  - Commissioning date inheritance with fallback before hierarchy propagation

- **Core domain model** (pure Python, no Django):
  - Entities: Coach, EMU, EMUConfiguration, Formation, MaintenanceUnit
  - Value objects: CoachType, UnitType
  - Services: GridProjectionService, MaintenanceProjectionService

- **Infrastructure**:
  - Docker Compose for PostgreSQL (port 5434)
  - Tailwind CSS v4 theme
  - Navbar with Trenes Argentinos branding

- **Testing**: 214 tests (97% coverage on core/services/)
  - Grid projection: 20 tests
  - Maintenance projection: 31 tests
  - Fleet views: 24 tests
  - PostgreSQL extractor: 26 tests
  - Access connection: 17 tests
  - Stub data: 22 tests
  - Domain entities: 74 tests
  - Integration tests marked with `@pytest.mark.integration` (excluded by default)

- **Documentation**:
  - ADR: projection grid design (`docs/decisions/projection_grid.md`)
  - ADR: Access to PostgreSQL staging migration (`docs/decisions/access_to_postgres_staging.md`)
  - Access connection guide with troubleshooting (`docs/access_connection.md`)
  - PostgreSQL Docker setup (`docs/postgres_docker.md`)
  - Maintenance cycle reference (`docs/maintenance_cycle.md`)
  - Business rules in Spanish (`context/grilla_proyeccion.md`)
  - Legacy DB schema introspection (`docs/legacy_bd/introspection/`)
  - UI screenshots (`docs/ui/`)

- **Utility scripts** (`scripts/`):
  - Database connection test
  - Local/remote DB path toggle

[Unreleased]: https://github.com/salamonepablo/ARS_MP/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/salamonepablo/ARS_MP/releases/tag/v1.0.0
