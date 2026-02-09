# PostgreSQL Docker Setup

This project supports running PostgreSQL locally via Docker with no external cost.

## Why

- Keep development dependencies local and reproducible.
- Avoid external managed databases or paid services.

## Usage

1. Start the database:

```powershell
docker compose up -d db
```

2. Configure environment variables (example):

```
DJANGO_DB_ENGINE=postgres
POSTGRES_DB=ars_mp
POSTGRES_USER=ars_mp
POSTGRES_PASSWORD=ars_mp
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

3. Apply migrations:

```powershell
py manage.py migrate
```

## Notes

- The database persists in a local Docker volume: `ars_mp_postgres_data`.
- For CI or local runs without Docker, SQLite remains the default.
