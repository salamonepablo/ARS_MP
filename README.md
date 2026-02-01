# ARS_MP — Argentinian Rolling Stock Maintenance Planner

Sistema de proyeccion y planificacion de mantenimiento ferroviario para material rodante argentino.
Enfoque: **ETL** desde fuentes legacy (Access/CSV/Excel) y **visualizacion web**.

## Estado actual

- Estructura base creada (capas `core/`, `etl/`, `web/`, `infrastructure/`, `tests/`, `docs/`).
- Documentacion inicial y fuentes de prueba disponibles en `docs/legacy_bd/`.

## Stack

| Componente | Tecnologia |
|------------|------------|
| Lenguaje | Python 3.11+ |
| Framework Web | Django 5.0+ |
| Base de Datos | PostgreSQL 15+ |
| ETL | pandas, openpyxl, pyodbc/sqlalchemy-access |
| Frontend | Django Templates + HTMX + Alpine.js |
| Estilos | Tailwind CSS |
| Contenedores | Docker + Docker Compose |
| Testing | pytest + coverage |

## Arquitectura (Clean Architecture + DDD simplificado)

- `core/`: dominio y logica de negocio (Python puro, sin Django)
- `etl/`: extractores/transformadores/loaders hacia PostgreSQL
- `web/`: apps Django (UI + endpoints)
- `infrastructure/`: implementaciones concretas (DB, integraciones externas)

```
ARS_MP/
├── core/
│   ├── domain/
│   ├── interfaces/
│   └── services/
├── etl/
│   ├── extractors/
│   ├── transformers/
│   └── loaders/
├── infrastructure/
│   ├── database/
│   └── external/
├── web/
│   ├── fleet/
│   ├── projections/
│   ├── reports/
│   └── api/
├── tests/
├── docs/
└── context/
```

## Quickstart (desarrollo)

### 1) Crear entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Instalar dependencias (minimas iniciales)

> Nota: este proyecto ira incorporando dependencias a medida que se implementen features.

```powershell
pip install django pandas openpyxl pytest pytest-cov
```

### 3) Ejecutar tests

```powershell
pytest
```

## Datos legacy de ejemplo

En `docs/legacy_bd/` hay archivos `.mdb/.accdb` y CSV de prueba usados para el desarrollo de ETL.

## Documentacion

- Documentacion tecnica: `docs/` (en ingles)
- Reglas/criterios de negocio: `context/` (en espanol)

Cada feature implementada debe dejar:

- Codigo + tests
- Un apunte breve en `docs/` o `context/` segun corresponda

## Convenciones

- Codigo en ingles (nombres de funciones/variables)
- Docstrings estilo Google
- `core/` no depende de Django
- Django Models con `verbose_name` en espanol (cuando se agreguen modelos)
- ETL con manejo explicito de errores

## Versionado

- Commits atomicos y con Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- No subir secretos (`.env`, credenciales)

## Licencia

Pendiente.
