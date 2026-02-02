# ARS_MP — Argentinian Rolling Stock Maintenance Planner

Sistema de proyeccion y planificacion de mantenimiento ferroviario para material rodante argentino.
Enfoque: **ETL** desde fuentes legacy (Access/CSV/Excel) y **visualizacion web**.

## Estado actual

- Estructura base creada (capas `core/`, `etl/`, `web/`, `infrastructure/`, `tests/`, `docs/`).
- Documentacion inicial y fuentes de prueba disponibles en `docs/legacy_bd/`.
- **Vista de flota** con 111 tarjetas de modulos (CSR + Toshiba) con datos mock.

## Stack

| Componente | Tecnologia |
|------------|------------|
| Lenguaje | Python 3.11+ |
| Framework Web | Django 5.0+ |
| Base de Datos | PostgreSQL 15+ (SQLite en dev) |
| ETL | pandas, openpyxl, pyodbc |
| Frontend | Django Templates + HTMX + Alpine.js |
| Estilos | Tailwind CSS v4 |
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
├── theme/              # Tailwind CSS theme
├── templates/          # Base templates
├── tests/
├── docs/
└── context/
```

## Quickstart (desarrollo)

### 1) Crear entorno virtual

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Instalar dependencias Python

```powershell
pip install -r requirements.txt
```

### 3) Instalar dependencias Node.js (Tailwind CSS)

```powershell
cd theme/static_src
npm install
npm run build
cd ../..
```

### 4) Ejecutar migraciones

```powershell
py manage.py migrate
```

### 5) Iniciar servidor de desarrollo

```powershell
py manage.py runserver
```

Acceder a: **http://127.0.0.1:8000/fleet/modules/**

### 6) (Opcional) Modo desarrollo con hot-reload de CSS

En una terminal separada:

```powershell
cd theme/static_src
npm run dev
```

## Vista de Flota

La vista principal muestra **111 tarjetas** de modulos:

- **86 Modulos CSR** (M01-M86)
  - M01-M42: Cuadruplas (4 coches)
  - M43-M86: Triplas (3 coches)
- **25 Modulos Toshiba** (T01-T25)
  - T01-T12: Cuadruplas (4 coches)
  - T13-T25: Triplas (3 coches)

Cada tarjeta muestra:
- Kilometraje del mes actual
- Kilometraje total acumulado
- Ultimo mantenimiento (tipo, fecha, dias transcurridos)
- KM desde ultimo mantenimiento

### Filtros disponibles

- `/fleet/modules/` - Todos los modulos
- `/fleet/modules/?fleet=csr` - Solo CSR
- `/fleet/modules/?fleet=toshiba` - Solo Toshiba

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
