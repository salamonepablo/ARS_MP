# AGENTS.md - ARS_MP (Argentinian Rolling Stock Maintenance Planner)

> Instructions for AI coding agents. Respond in **Spanish**. Code, docstrings, and technical docs in **English**.

## Quick Reference

```bash
# Setup
.venv\Scripts\activate          # Windows virtualenv
pip install -r requirements.txt
docker compose up -d && python manage.py migrate

# Dev
python manage.py runserver
cd theme/static_src && npm run dev  # Tailwind watch

# Test (single)
pytest tests/path/to/test_file.py::TestClass::test_method

# Test (all)
pytest                          # unit tests only (default)
pytest -m integration           # Access DB tests
pytest --cov=core --cov=etl     # with coverage
```

## Project Structure

```
ARS_MP/
├── core/                  # Pure Python domain (NO Django imports)
│   ├── domain/entities/   # @dataclass: Coach, EMU, Formation, EmuConfiguration
│   ├── domain/value_objects/  # Enums: UnitType, CoachType
│   └── services/          # Stateless @staticmethod services
├── etl/extractors/        # Access/Postgres data extraction
├── infrastructure/
│   ├── database/models.py     # Django ORM (domain + staging)
│   └── database/repositories.py  # Repository pattern
├── web/fleet/             # Views, templates, URLs
├── config/                # settings.py, urls.py
└── tests/                 # Mirrors source structure
```

**Dependencies**: `core/` → nothing | `infrastructure/` → `core/` + Django | `etl/` → all | `web/` → all

## Code Style

### Imports
```python
# 1. stdlib
from datetime import date
from dataclasses import dataclass

# 2. third-party
from django.db import models

# 3. local (relative within package, absolute across packages)
from .module import X
from core.domain.entities.coach import Coach
```

Use `TYPE_CHECKING` guard for circular imports in domain entities.

### Type Hints (Required)
- Modern syntax in `core/`: `int | None`, `list[str]`, `dict[str, Any]`
- `Optional[X]` acceptable in `etl/` and `infrastructure/`
- Use `Literal["CSR", "Toshiba"]` for constrained strings
- `from __future__ import annotations` in services for forward refs

### Docstrings (Google format)
```python
def project_intervention(fleet_type: Literal["CSR", "Toshiba"], km: int) -> Result | None:
    """Calculate next maintenance intervention.

    Args:
        fleet_type: "CSR" or "Toshiba".
        km: Current total accumulated km.

    Returns:
        ProjectionResult for soonest-expiring cycle, or None.

    Raises:
        ValueError: If fleet_type unrecognized.
    """
```
Test docstrings in **Spanish** (business context).

### Naming
| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `Coach`, `StgModulo` |
| Functions | snake_case | `get_modules()` |
| Private | `_` prefix | `_validate()` |
| Constants | UPPER_SNAKE | `AVG_DAILY_KM` |
| Django models | `Model` suffix / `Stg` prefix | `EmuModel`, `StgKilometraje` |

### Django Models
- UUID primary keys: `models.UUIDField(primary_key=True, default=uuid.uuid4)`
- `verbose_name` in Spanish on every field
- `Meta` with `db_table`, `verbose_name`, `ordering`
- `__str__` on every model
- Timestamps: `created_at = DateTimeField(auto_now_add=True)`

### Domain Entities
```python
@dataclass(kw_only=True)
class Coach(MaintenanceUnit):
    coach_type: CoachType
    seating_capacity: int

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.seating_capacity <= 0:
            raise ValueError("seating_capacity must be positive")
```
- Pure `@dataclass(kw_only=True)`, no Django imports
- Self-validating via `__post_init__` → `_validate()`
- `@dataclass(frozen=True)` for immutable value objects

### Error Handling
- Domain: `ValueError` with descriptive messages
- Infrastructure: custom exceptions with `from e` chaining
- ETL: tiered fallback (Postgres → Access → stub) with logging
- Use `logger.warning()` for fallbacks, `logger.error()` for failures
- Close connections in `finally` blocks

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.warning("Failed to connect: %s", error)  # %-formatting
```

### Tests
- Mirror source structure: `tests/core/domain/entities/test_coach.py`
- Group in `Test*` classes with Spanish docstrings
- Fixtures in `conftest.py`
- Markers: `@pytest.mark.django_db`, `@pytest.mark.integration`
- Mock externals with `unittest.mock.patch`

## Git

- **Commits**: Conventional (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`)
- **Never commit**: `.env`, `*.mdb`, `*.accdb`, `db.sqlite3`, credentials
- **Tags**: semver `v1.0.0`

## Environment

| Component | Version/Config |
|-----------|----------------|
| Python | 3.11+ |
| Django | 5.0+ |
| PostgreSQL | 15+ (Docker port 5434) |
| DB toggle | `DJANGO_DB_ENGINE=postgres` or SQLite fallback |
| Access DB | `LEGACY_ACCESS_DB_PATH` env var, ODBC required |

## CI Pipeline (.github/workflows/ci.yml)

Runs on push/PR: `python manage.py check` → `makemigrations --check` → `pytest -q`
