# Legacy Access Database Connection

This document describes how ARS_MP connects to the legacy Microsoft Access database for extracting fleet module data.

## Overview

The ETL module provides a read-only connection to legacy Access databases (`.mdb`, `.accdb`) used by the existing maintenance management system. The connection is designed with safety and fallback behavior in mind.

## Requirements

### ODBC Driver

The Microsoft Access ODBC driver must be installed on the system:

- **Driver name**: `Microsoft Access Driver (*.mdb, *.accdb)`
- **Download**: [Microsoft Access Database Engine 2016 Redistributable](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
- **Architecture**: Use 64-bit version if running 64-bit Python

To verify the driver is installed:

```python
import pyodbc
print([d for d in pyodbc.drivers() if 'Access' in d])
```

### Environment Variables

Configure the following in your `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `LEGACY_ACCESS_DB_PATH` | Yes | Path to the `.accdb` file (relative or absolute) |
| `LEGACY_ACCESS_DB_PASSWORD` | No | Database password (if protected) |
| `LEGACY_ACCESS_ODBC_DRIVER` | No | Override driver name (auto-detected by default) |

Example `.env`:

```env
LEGACY_ACCESS_DB_PATH=docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1.accdb
# LEGACY_ACCESS_DB_PASSWORD=  # Leave empty for unprotected databases
```

## Architecture

### Module Structure

```
etl/extractors/
├── access_connection.py   # Connection management
├── access_extractor.py    # Data extraction logic
└── access_introspect.py   # Schema introspection tool
```

### Connection Flow

```
1. Check is_access_available()
   ├── Verify LEGACY_ACCESS_DB_PATH is set
   ├── Verify file exists
   └── Verify ODBC driver is installed

2. get_access_connection()
   ├── Build connection string with ReadOnly=1
   ├── Add password if LEGACY_ACCESS_DB_PASSWORD is set
   └── Return pyodbc.Connection

3. get_modules_from_access()
   ├── Query A_00_Módulos for module list
   ├── Query A_00_Kilometrajes for km data
   ├── Query A_00_OT_Simaf for maintenance events
   └── Transform to ModuleData objects
```

### Fallback Behavior

The `get_modules_with_fallback()` function provides graceful degradation:

1. **Access available**: Returns real data from the database
2. **Access unavailable**: Returns stub data with a warning log

This ensures the application always works, even without the database.

Reasons for fallback:
- Database file not found
- ODBC driver not installed
- Environment variables not configured
- Connection or query errors

## Safety Measures

### Read-Only Connection

All connections include `ReadOnly=1` in the connection string to prevent any accidental modifications to the legacy database.

### No Secrets in Repository

- `.env` is gitignored
- `.env.example` provides a template without sensitive data
- Password is optional and only used at runtime

## Database Schema

Key tables used for extraction:

| Table | Purpose |
|-------|---------|
| `A_00_Módulos` | Module list with vehicle class |
| `A_00_Clase_Vehículo` | Fleet type (CSR, Toshiba) |
| `A_00_Kilometrajes` | Kilometraje readings by date |
| `A_00_OT_Simaf` | Maintenance events (OT records) |

For full schema documentation, see `docs/legacy_bd/introspection/`.

## Testing

### Unit Tests

Tests are designed to work without the real database:

```bash
pytest tests/test_access_connection.py -v
```

### Integration Tests

Integration tests require the database and are skipped when unavailable:

```bash
# These will be skipped if database is not configured
pytest tests/test_access_connection.py::TestIntegrationWithRealDatabase -v
```

## Troubleshooting

### "No suitable Access ODBC driver found"

Install the Microsoft Access Database Engine:
- Download from [Microsoft](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
- Use the same architecture as your Python installation (32-bit or 64-bit)

### "Access database file not found"

- Verify the path in `LEGACY_ACCESS_DB_PATH`
- Use forward slashes or escaped backslashes in paths
- Relative paths are resolved from the project root

### "Authentication failed"

- Check `LEGACY_ACCESS_DB_PASSWORD` if the database is protected
- For unprotected databases, leave the password empty or unset
