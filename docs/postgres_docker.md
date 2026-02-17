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

- The database persists in a local Docker volume: `ars_mp_postgres`.
- For CI or local runs without Docker, SQLite remains the default.

## Quick table inspection from Docker Desktop terminal

If your PostgreSQL container is running (for example, `ars_mp_postgres`), you can inspect any table with:

```powershell
docker exec -it ars_mp_postgres psql -U ars_mp -d ars_mp -c "SELECT * FROM your_table_name LIMIT 20;"
```

Useful additional commands:

```powershell
# List all tables in the public schema
docker exec -it ars_mp_postgres psql -U ars_mp -d ars_mp -c "\dt"

# Show table structure (columns and types)
docker exec -it ars_mp_postgres psql -U ars_mp -d ars_mp -c "\d+ your_table_name"
```

Tip: if your container has a different name, run `docker ps` first and replace `ars_mp_postgres` with the actual container name.
