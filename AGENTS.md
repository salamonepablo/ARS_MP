# AGENTS.md - ARS_MP (Argentinian Rolling Stock Maintenance Planner)

> Instructions for AI coding agents operating in this repository.
> Respond in **Spanish**. Write code, variable names, docstrings, and technical docs in **English**.
> Business rules and context docs go in **Spanish** (in `context/`).

## Build & Run Commands

```bash
# Activate virtualenv (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database (PostgreSQL via Docker on port 5434)
docker compose up -d
python manage.py migrate

# Dev server
python manage.py runserver

# Tailwind CSS (from theme/static_src/)
npm run dev    # watch mode
npm run build  # production build
```

## Test Commands

```bash
# Run all unit tests (excludes @pytest.mark.integration by default)
pytest

# Run a single test file
pytest tests/test_grid_projection.py

# Run a single test class
pytest tests/core/domain/entities/test_coach.py::TestCoachCreation

# Run a single test function
pytest tests/core/domain/entities/test_coach.py::TestCoachCreation::test_create_motor_coach_csr

# Run tests with coverage (minimum 80% on core/)
pytest --cov=core --cov=etl

# Run integration tests (requires Access DB connection)
pytest -m integration

# Run only unit tests (default behavior, explicit)
pytest -m "not integration"

# Verbose with short tracebacks (already in pytest.ini defaults)
pytest -v --tb=short
```

**pytest.ini config**: `DJANGO_SETTINGS_MODULE=config.settings`, test discovery in `tests/`, pattern `test_*.py`, classes `Test*`, functions `test_*`.

## Project Architecture

```
ARS_MP/
├── core/                  # Pure Python domain (NO Django imports allowed)
│   ├── domain/entities/   # @dataclass entities: Coach, EMU, Formation, EmuConfiguration
│   ├── domain/value_objects/  # Enums: UnitType, CoachType
│   ├── services/          # Stateless services (all @staticmethod)
│   └── interfaces/        # Abstract contracts (reserved)
├── etl/extractors/        # Access/Postgres data extraction
├── infrastructure/
│   ├── database/models.py     # Django ORM models (domain + staging)
│   ├── database/repositories.py  # Repository pattern (model<->entity conversion)
│   └── database/management/commands/  # sync_access command
├── web/fleet/             # Django views, templates, URLs
├── config/                # Django project: settings.py, urls.py
├── tests/                 # Mirrors source structure
└── docs/, context/        # Technical docs (EN) and business rules (ES)
```

**Dependency rule**: `core/` -> nothing | `infrastructure/` -> `core/` + Django | `etl/` -> `core/` + `infrastructure/` | `web/` -> all

## Code Style

### Imports
Three groups separated by blank lines: (1) stdlib, (2) third-party, (3) local project.
Use relative imports within the same package (`from .module import X`).
Use absolute imports across packages (`from core.domain.entities.coach import Coach`).
Use `TYPE_CHECKING` guard for circular import avoidance in domain entities.

### Type Hints
- Required on all function signatures (parameters + return type).
- Prefer modern syntax in `core/`: `int | None`, `list[str]`, `dict[str, Any]`.
- `Optional[X]` is acceptable in `etl/` and `infrastructure/` layers.
- Use `Literal["CSR", "Toshiba"]` for constrained string values.
- Use `from __future__ import annotations` in service files for forward refs.

### Docstrings (Google format)
```python
def project_next_intervention(fleet_type: Literal["CSR", "Toshiba"], km_total: int) -> ProjectionResult | None:
    """Calculate the next maintenance intervention.

    Args:
        fleet_type: "CSR" or "Toshiba".
        km_total: Current total accumulated km.

    Returns:
        ProjectionResult for the soonest-expiring cycle, or None if no data.

    Raises:
        ValueError: If fleet_type is not recognized.
    """
```
- Every module file gets a module-level docstring.
- Test docstrings are written in **Spanish** (business context).

### Naming Conventions
| Element           | Convention        | Example                              |
|-------------------|-------------------|--------------------------------------|
| Classes           | PascalCase        | `Coach`, `EmuModel`, `StgModulo`     |
| Functions/methods | snake_case        | `get_modules_from_access()`          |
| Private helpers   | `_` prefix        | `_validate()`, `_parse_date()`       |
| Constants         | UPPER_SNAKE_CASE  | `AVG_DAILY_KM`, `CSR_MAINTENANCE_CYCLES` |
| Enums             | PascalCase class, UPPER values | `UnitType.COACH`        |
| Django models     | `Model` suffix (domain), `Stg` prefix (staging) | `EmuModel`, `StgKilometraje` |
| DB tables         | snake_case        | `fleet_emu`, `stg_modulo`            |

### Django Models
- UUID primary keys (`models.UUIDField(primary_key=True, default=uuid.uuid4)`).
- `verbose_name` in **Spanish** on every field.
- `Meta` class on every model with `db_table`, `verbose_name`, `ordering`.
- `__str__` on every model.
- Auto-timestamps: `created_at = DateTimeField(auto_now_add=True)`, `updated_at = DateTimeField(auto_now=True)`.
- Staging models use `UniqueConstraint` and `Index` in Meta.

### Domain Entities
- Pure `@dataclass(kw_only=True)` with no Django dependencies.
- Self-validating via `__post_init__` -> `_validate()`.
- Use `@dataclass(frozen=True)` for immutable value objects.
- Abstract base: `MaintenanceUnit(ABC)` with abstract `get_unit_type()`.

### Error Handling
- Domain validation: raise `ValueError` with descriptive messages.
- Infrastructure: custom exceptions (e.g., `AccessConnectionError`) with `from e` chaining.
- ETL: tiered fallback pattern (Postgres -> Access ODBC -> stub data) with logging at each level.
- Use `logger.warning()` for recoverable fallbacks, `logger.error()` for unexpected failures.
- Always close connections in `finally` blocks.

### Logging
- Module-level: `logger = logging.getLogger(__name__)`.
- Three configured loggers: `etl`, `core`, `web` (levels via env vars).
- Use %-formatting for lazy evaluation: `logger.warning("Failed: %s", error)`.

### Tests
- Mirror source structure under `tests/`.
- Group related tests in `Test*` classes with descriptive docstrings (Spanish).
- Use `conftest.py` for fixtures and factory functions.
- Mark Django DB tests with `@pytest.mark.django_db`.
- Mark Access DB tests with `@pytest.mark.integration`.
- Use `unittest.mock.patch` for external dependency mocking.

## Git & Documentation

- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`). Small, atomic.
- **Never commit**: `.env`, credentials, `*.mdb`, `*.accdb`, `db.sqlite3`.
- **Tags**: semantic versioning (`v1.0.0`). Update `docs/CHANGELOG.md` at milestones.
- **Technical docs**: English, in `docs/`. ADRs in `docs/decisions/`.
- **Business docs**: Spanish, in `context/`.

## Environment

- **Python**: 3.11+ | **Django**: 5.0+ | **PostgreSQL**: 15+ (Docker, port 5434)
- **Settings**: single `config/settings.py`, configured via env vars (see `.env.example`)
- **DB toggle**: set `DJANGO_DB_ENGINE=postgres` for PostgreSQL, unset for SQLite fallback
- **Access DB**: path in `LEGACY_ACCESS_DB_PATH` env var, requires ODBC driver
