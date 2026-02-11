# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **ETL Staging Infrastructure**: PostgreSQL staging tables (`Stg*` models) as mirrors of legacy Access data
- **sync_access command**: Management command to sync Access → PostgreSQL with incremental updates
- **postgres_extractor**: Query staging tables for web views, replacing direct ODBC access
- **Maintenance Hierarchy**: Higher interventions override lower ones (RG > RB > MEN for Toshiba, DA > PE > BA > AN for CSR)
- **Inheritance Tracking**: `inherited_from` field shows when dates/km come from a higher intervention
- **Sync Status Bar**: Real-time sync status indicator in fleet list with AJAX polling
- **Heavy Maintenance View**: Module detail shows only heavy cycles (RB/RG, AN/BA/PE/DA) with clear indicators
- SyncLog model to track sync runs, stats, and errors
- Database logging configuration for debugging

### Changed

- Fleet views now read from PostgreSQL staging tables instead of direct ODBC queries
- Module detail template reorganized to focus on heavy maintenance projections
- access_extractor.py improved with better ODBC handling and error messages

### Fixed

- Nothing yet

---

## Version History

_No releases yet. First release will be tagged as `v0.1.0` when Django project is initialized and basic ETL is functional._
