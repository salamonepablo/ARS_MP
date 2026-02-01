## 🚀 2 - Git y README.md (prompt para IA)

### Objetivo

Dejar el repo local listo para trabajar desde **Windows + PowerShell 7**, con:

- Git inicializado en la raíz del proyecto.
- Remoto `origin` apuntando al repo ya creado.
- `.gitignore` adecuado para Python/Django/ETL.
- `README.md` inicial alineado con el estado actual del proyecto (estructura ya creada) y con el stack definido.
- Primer commit en rama `main` y push al remoto.

### Contexto

- Proyecto: `ARS_MP` (Argentinian Rolling Stock Maintenance Planner)
- Carpeta raíz (Windows): `C:\Programmes\TFM\ARS_MP`
- Remoto ya creado:
	- https://github.com/salamonepablo/ARS_MP.git
- Shell: **PowerShell 7 (`pwsh`)**
- Convenciones del proyecto (según `AGENTS.md`):
	- Responder en español
	- Código en inglés (nombres de funciones/variables)
	- Docstrings estilo Google
	- `core/` no depende de Django
	- Documentación técnica en inglés; documentación/reglas de negocio en español
	- Versionado prolijo (commits atómicos + Conventional Commits)

### Instrucciones para la IA

Actuá como developer senior. Usá comandos compatibles con **PowerShell 7** (no bash). Si algún paso ya está hecho, no lo repitas: validalo y seguí.

Además:

- No incluyas secretos/credenciales.
- Mantené commits pequeños y con intención clara.
- Mientras creás el baseline, dejá preparada la base para documentar lo implementado en `docs/`.

#### 1) Verificación rápida (sin romper nada)

Ejecutá en la raíz del proyecto:

```powershell
Set-Location "C:\Programmes\TFM\ARS_MP"
git --version
Test-Path .git
```

- Si `Test-Path .git` devuelve `True`, Git ya está inicializado.
- Si devuelve `False`, inicializalo en el siguiente paso.

#### 2) Inicializar Git y rama principal

Si `.git` no existe:

```powershell
git init
git branch -M main
```

Si ya existe `.git`, asegurate de estar en `main`:

```powershell
git branch -M main
```

#### 3) Configurar el remoto `origin` (remoto ya creado)

Validá primero si ya existe `origin`:

```powershell
git remote -v
```

- Si `origin` no existe, agregalo:

```powershell
git remote add origin https://github.com/salamonepablo/ARS_MP.git
```

- Si `origin` existe pero apunta a otra URL, corregilo:

```powershell
git remote set-url origin https://github.com/salamonepablo/ARS_MP.git
```

#### 4) Crear `.gitignore`

Crear en la raíz un archivo `.gitignore` con contenido para Python/Django/pytest/ETL.

Requisitos mínimos:

- Ignorar entornos virtuales: `venv/`, `.venv/`
- Ignorar cachés: `__pycache__/`, `*.pyc`, `.pytest_cache/`
- Ignorar coverage: `.coverage`, `htmlcov/`, `.ruff_cache/`, `.mypy_cache/`
- Ignorar secretos: `.env`, `.env.*` (excepto `.env.example` si se agrega)
- Ignorar artefactos Django: `staticfiles/`, `media/` (si existen)
- Ignorar archivos de editor/OS: `.vscode/` (opcional), `Thumbs.db`, `.DS_Store`

Nota: no ignores el código ni carpetas `core/`, `etl/`, `web/`, `docs/`, `tests/`.

Sugerencia: no ignores `docs/legacy_bd/` por ahora (se usa como fuente de prueba), pero revisá tamaño/privacidad antes de hacer público el repo.

#### 5) Crear `README.md` inicial

Crear `README.md` en la raíz con el siguiente contenido (ajustado al estado actual del repo: estructura creada, Django todavía puede no estar inicializado).

```markdown
# ARS_MP — ARS Maintenance Planner

Sistema de proyección y planificación de mantenimiento ferroviario para material rodante argentino.
Enfoque: **ETL** desde fuentes legacy (Access/CSV/Excel) y **visualización web**.

## Estado actual

- Estructura base creada (capas `core/`, `etl/`, `web/`, `infrastructure/`, `tests/`, `docs/`).
- Documentación inicial y fuentes de prueba disponibles en `docs/legacy_bd/`.

## Stack

- Python 3.11+
- Django 5+
- PostgreSQL 15+
- ETL: pandas, openpyxl (y conectores para Access según disponibilidad)
- Frontend: Django Templates + HTMX + Alpine.js
- Estilos: Tailwind CSS
- Testing: pytest + coverage

## Arquitectura (Clean Architecture + DDD simplificado)

- `core/`: dominio y lógica de negocio (Python puro, sin Django)
- `etl/`: extractores/transformadores/loaders hacia PostgreSQL
- `web/`: apps Django (UI + endpoints)
- `infrastructure/`: implementaciones concretas (DB, integraciones externas)

Estructura:

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
└── docs/
```

## Quickstart (desarrollo)

### 1) Crear entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Instalar dependencias (mínimas iniciales)

> Nota: este proyecto irá incorporando dependencias a medida que se implementen features.

```powershell
pip install django pandas openpyxl pytest pytest-cov
```

### 3) Ejecutar tests

```powershell
pytest
```

## Datos legacy de ejemplo

En `docs/legacy_bd/` hay archivos `.mdb/.accdb` y CSV de prueba usados para el desarrollo de ETL.

## Documentación

- Documentación técnica: `docs/` (en inglés)
- Reglas/criterios de negocio: `context/` (en español)

Cada feature implementada debe dejar:

- Código + tests
- Un apunte breve en docs/context según corresponda

## Convenciones

- Código en inglés (nombres de funciones/variables)
- Docstrings estilo Google
- `core/` no depende de Django
- Django Models con `verbose_name` en español (cuando se agreguen modelos)
- ETL con manejo explícito de errores

## Versionado

- Commits atómicos y con Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- No subir secretos (`.env`, credenciales)

## Licencia

Pendiente.
```

Opcional (recomendado): crear un `docs/CHANGELOG.md` inicial con una sección `Unreleased`.

#### 6) Primer commit y push

Agregar archivos y crear el primer commit:

```powershell
git status
git add .
git commit -m "chore: initial scaffold + README"
```

Hacer push al remoto:

```powershell
git push -u origin main
```

#### 7) Checklist de salida

Confirmá:

```powershell
git remote -v
git status
git log --oneline -n 3
```

Entregables esperados:

- `.gitignore`
- `README.md`
- Repo inicializado, remoto configurado, commit creado y push a `main`.

