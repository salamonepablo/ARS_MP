# Access to Postgres staging plan

Date: 2026-02-10
Status: Proposal

## Context
The current detail view queries the legacy Access database directly through ODBC.
This path is fragile (driver limitations, schema quirks, lookup fields) and
requires defensive SQL for each screen. It also makes debugging and performance
harder, especially when we need joins or advanced filtering.

## Proposal
Introduce a staging layer in PostgreSQL that mirrors the Access tables (raw
ingestion). All business logic and projections would run against Postgres,
while Access is only used as a source system.

## Why this helps
- Stable SQL, better error messages, and predictable query behavior.
- Faster joins and indexing for projections and history views.
- Easier to test and to build incremental ETL routines.
- Clear separation: Access = source, Postgres = operational data store.

## Risks / Costs
- Initial mapping of Access schema into Postgres tables.
- Need to define incremental sync logic (by date or change tracking).
- Extra operational component (scheduled ETL runs).

## Suggested approach
1. Create raw staging tables in Postgres that mirror Access tables.
2. Build an ETL job to pull new/changed rows 1-3 times per day.
3. Add views/materialized views for projections and dashboards.
4. Update Django queries to read from Postgres instead of Access.

## Open questions
- Best incremental key per table (Fecha_Fin, Fecha, updated_at, etc.).
- Sync frequency aligned with operational shifts.
- Ownership of ETL scheduling (cron vs. Django management command).
