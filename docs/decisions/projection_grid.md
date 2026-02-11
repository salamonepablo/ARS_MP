# Projection Grid Architecture

## Decision

Implement a monthly maintenance projection grid as a view within the
existing `web.fleet` app (not a separate app), accessible from the
fleet module list via a "Man. Planner" button.

## Context

The railway maintenance team needs to project, month by month, when
each module will reach its next maintenance threshold.  The projection
must visualise the information in an Excel-like grid with colour-coded
cells (semaphore) and allow interactive editing (marking planned
interventions that reset lower cycles).

## Architecture

### Core Layer (`core/services/grid_projection.py`)

Pure Python service with **zero Django dependencies**.  Contains:

- `GridProjectionService` — static methods for projection calculations
- `MonthProjection`, `CycleRow`, `ModuleGridData` — immutable data objects
- `CYCLE_COLORS` — Tailwind CSS class mapping per cycle type
- `DEFAULT_MONTHS = 18`, `DEFAULT_AVG_MONTHLY_KM` — fleet constants

The projection algorithm:

1. For each module, iterate over heavy cycles (AN/BA/PE/DA for CSR,
   RB/RG for Toshiba).
2. Start from current `km_since` (km accumulated since last intervention).
3. Current month: prorate by remaining days
   (`avg_monthly_km / days_in_month * days_remaining`).
4. Subsequent months: add full `avg_monthly_km`.
5. Flag `exceeded = True` when accumulated km >= cycle threshold.

### Web Layer

- **View**: `projection_grid` at `/fleet/planner/`
- **Export**: `projection_export` at `/fleet/planner/export/`
- **Template**: `fleet/projection_grid.html` with Alpine.js interactivity
- **Button**: "Man. Planner" added to `module_list.html`

### Interaction (Double-Click)

Implemented client-side with Alpine.js:

1. Double-click a cell → replaces km with cycle code (e.g. "AN")
2. All lower-hierarchy cycles at that month reset to 0
3. Subsequent months recalculate from 0 with avg monthly km
4. Double-click again → restores original values

State is tracked in `interventions` object: `{ "M01-AN-3": true }`.

### Excel Export

Uses `openpyxl` to generate .xlsx with:

- Matching colour fills per cycle type
- Number formatting (`#,##0`)
- Frozen panes (header + sticky columns)
- Merged cells for module IDs

## Colour Mapping

| Cycle | Tailwind BG | Tailwind Text | Excel Fill | Excel Font |
|-------|------------|--------------|------------|------------|
| AN | bg-green-100 | text-green-800 | DCFCE7 | 166534 |
| BA | bg-yellow-100 | text-yellow-800 | FEF9C3 | 854D0E |
| PE | bg-sky-100 | text-sky-800 | E0F2FE | 075985 |
| DA | bg-red-100 | text-red-800 | FEE2E2 | 991B1B |
| RB | bg-yellow-100 | text-yellow-800 | FEF9C3 | 854D0E |
| RG | bg-red-100 | text-red-800 | FEE2E2 | 991B1B |

## URLs

```
GET /fleet/planner/?fleet=csr&months=18&avg_km=12000
GET /fleet/planner/export/?fleet=csr&months=18&avg_km=12000
```

## Files

```
core/services/grid_projection.py     # Pure business logic
web/fleet/views.py                   # projection_grid, projection_export
web/fleet/urls.py                    # planner/, planner/export/
web/fleet/templates/fleet/projection_grid.html
tests/test_grid_projection.py        # 17 tests
```
