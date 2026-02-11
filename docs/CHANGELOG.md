# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Maintenance Projection Grid** (`/fleet/planner/`):
  - Excel-like grid projecting km per heavy cycle per module, month by month
  - Fleet selector (CSR/Toshiba), configurable months (default 18) and avg km/month
  - Colour-coded semaphore: green (AN), yellow (BA/RB), sky-blue (PE), red (DA/RG)
  - Double-click to mark interventions with hierarchy reset (Alpine.js)
  - Excel export with matching colour format (`/fleet/planner/export/`)
  - Pure business logic in `core/services/grid_projection.py` (no Django deps)
  - 17 tests for grid projection service
- **ETL Staging Infrastructure**: PostgreSQL staging tables (`Stg*` models) as mirrors of legacy Access data
- **sync_access command**: Management command to sync Access → PostgreSQL with incremental updates
- **postgres_extractor**: Query staging tables for web views, replacing direct ODBC access
- **Maintenance Hierarchy**: Higher interventions override lower ones (RG > RB > MEN for Toshiba, DA > PE > BA > AN for CSR)
- **Inheritance Tracking**: `inherited_from` field shows when dates/km come from a higher intervention
- **Sync Status Bar**: Real-time sync status indicator in fleet list with AJAX polling
- **Heavy Maintenance View**: Module detail shows only heavy cycles (RB/RG, AN/BA/PE/DA) with clear indicators
- **Comprehensive Tests**: 211 tests total (97% coverage on core/services/)
- **Utility Scripts** (`scripts/`): DB connection test, local/remote path toggle
- SyncLog model to track sync runs, stats, and errors
- Database logging configuration for debugging

### Changed

- Fleet views now read from PostgreSQL staging tables instead of direct ODBC queries
- Module detail template reorganized to focus on heavy maintenance projections
- Navbar redesigned: white background with Trenes Argentinos logo
- access_extractor.py improved with better ODBC handling, BOM-safe CSV parsing

### Fixed

- Commissioning date inheritance: fallback applied before hierarchy propagation
- CSV encoding issue with BOM in URG-Modulos.csv (utf-8-sig)
- Test fallback assertion for logging with propagate=False

---

## Version History

_No releases yet. First release will be tagged as `v0.1.0` when all core features are functional._
