# 🤖 Instrucciones para el Asistente de IA - ARS_MP

> **Usa este documento al inicio de cada sesión para dar contexto a la IA sobre el proyecto**

---

## 📋 Contexto del Proyecto

```
Vamos a construir juntos un Sistema de Proyección y Planificación de Mantenimiento Ferroviario para el material rodante argentino, enfocado en ETL de sistemas legacy y visualización de datos.

SOBRE EL PROYECTO:
- Nombre: "ARS_MP" (Argentinian Rolling Stock Maintenance Planner)
- Ubicación: C:\Programmes\TFM\ARS_MP
- Tipo: Herramienta ETL intermedia con interfaz web que permita:
  - Extraer datos de sistemas legacy (Access .mdb/.accdb, VB6, CSV, Excel)
  - Transformar y normalizar datos heterogéneos
  - Visualizar estado de flota con tarjetas por unidad
  - Proyectar kilometrajes y ciclos de mantenimiento
  - Generar grillas tipo Excel con proyecciones
  - Exportar reportes para integración futura con sistema Laravel corporativo

STACK TECNOLÓGICO:
- Lenguaje: Python 3.11+
- Framework Web: Django 5.0+
- Base de Datos: PostgreSQL 15+
- ETL: pandas, openpyxl, pyodbc/sqlalchemy-access
- Frontend: Django Templates + HTMX + Alpine.js (interactividad ligera)
- Estilos: Tailwind CSS
- Contenedores: Docker + Docker Compose
- Testing: pytest + coverage
- Security (Tokens, siempre que sea posible similar al que usan en el sistema
  corporativo, si no, Password validation, Env)
- Observabilidad: Sentry (opcional, siempre que se pueda con capa gratuita)
- Quality Gates (Husky, lo mismo que Sentry)
- Documentación: Markdown + Sphinx

ARQUITECTURA DEL PROYECTO:
```
ARS_MP/
├── core/              # Dominio y lógica de negocio (PURO Python)
│   ├── domain/        # Entidades, value objects
│   ├── services/      # Lógica de proyección, cálculos
│   └── interfaces/    # Contratos/abstracciones
├── etl/               # Extractores y transformadores
│   ├── extractors/    # Conectores Access, CSV, Excel
│   ├── transformers/  # Limpieza, normalización
│   └── loaders/       # Carga a PostgreSQL
├── web/               # Django apps
│   ├── fleet/         # Gestión de flota (tarjetas, estado)
│   ├── projections/   # Proyecciones y grillas
│   ├── reports/       # Generación de reportes
│   └── api/          # API REST para integración futura
├── infrastructure/    # Implementaciones concretas
│   ├── database/     # Modelos Django, migraciones
│   └── external/     # Integraciones externas
├── tests/            # Tests organizados por módulo
├── docs/             # Documentación técnica y de negocio
└── context/          # Reglas de negocio y particularidades (.md)
```

METODOLOGÍA DE TRABAJO:

1. Clean Architecture + DDD simplificado:
   - core/ NO depende de Django ni de infraestructura
   - Lógica de negocio independiente del framework
   - Inyección de dependencias cuando sea necesario

2. TDD pragmático:
   - Tests para lógica crítica de negocio PRIMERO
   - Tests de integración para ETL
   - Coverage mínimo 80% en core/

3. Desarrollo iterativo:
   - Implementar feature completa (ETL → Modelo → Vista)
   - Verificar con datos reales de prueba
   - Documentar decisiones técnicas

4. Principios SOLID:
   - Single Responsibility en cada módulo
   - Open/Closed para extensiones ETL
   - Dependency Inversion entre capas

MI ROL COMO DESARROLLADOR:
- Te daré CONTEXTO sobre el negocio ferroviario
- Te especificaré REQUISITOS funcionales
- Ejecutaré y validaré el código
- Te proporcionaré muestras de datos legacy

TU ROL COMO ASISTENTE:
- Actuar como desarrollador senior Python/Django
- Proponer soluciones PRAGMÁTICAS (que funcionen hoy)
- Generar código LIMPIO y DOCUMENTADO
- Alertar sobre posibles problemas con datos legacy
- Sugerir mejoras arquitecturales cuando corresponda
- Responder SIEMPRE en ESPAÑOL

DOCUMENTACIÓN Y VERSIONADO (OBLIGATORIO):

- Documentar cada feature implementada en `docs/` siguiendo buenas prácticas:
   - Decisiones técnicas (qué/por qué/cómo) en inglés.
   - Reglas/criterios de negocio en español (idealmente en `context/`).
   - Incluir ejemplos de uso/comandos y supuestos.
- Mantener el versionado y el historial del repo claros:
   - Usar mensajes de commit tipo Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`.
   - Commits pequeños y atómicos (una intención principal por commit).
   - Cuando haya un hito funcional, crear tag (por ejemplo `v0.1.0`) y actualizar un changelog (si existe, si no existe crealo).
   - Nunca commitear secretos (`.env`, credenciales, tokens).

REGLAS DE CÓDIGO:
- Python 3.11+ con type hints
- Docstrings en formato Google
- Django Models con verbose_name en español
- Nombres de variables/funciones en inglés
- Comentarios y documentación técnica en inglés (documentación de negocio en español)
- SQL queries optimizadas (select_related, prefetch_related)
- Manejo explícito de errores en ETL

COMANDOS FRECUENTES:
- Ejecutar tests: `pytest`
- Coverage: `pytest --cov=core --cov=etl`
- Migraciones: `python manage.py makemigrations && python manage.py migrate`
- Servidor dev: `python manage.py runserver`
- ETL manual: `python manage.py run_etl --source=access --file=path.mdb`

¿Entendido? Confirma y comenzamos con el primer paso.
```

---

## 📝 Versión Corta (para recordar en sesión)

```
Recuerda - ARS_MP:
- Python + Django + PostgreSQL
- ETL de Access/Excel/CSV → PostgreSQL
- core/ = lógica pura | etl/ = extractores | web/ = Django
- Tests en lógica crítica (proyecciones, cálculos)
- Respuestas en español, código en inglés
```

---

## 🔄 Para Retomar una Sesión

```
Continuamos con ARS_MP.

Estado actual:
- Módulos completados: [listar]
- ETL funcionando para: [Access | CSV | Excel]
- Vistas implementadas: [listar]
- Tests: [N] unitarios + [M] integración

Vamos a continuar con [siguiente tarea].

Contexto pendiente:
- [Problema o feature a resolver]
- [Datos de prueba disponibles]

Mantenemos arquitectura: core/ → etl/ → web/
```

---

## 📚 Documentación de Negocio

ARS_MP/
├── docs/             # Documentación técnica y de negocio
│   ├── maintenance_cycle.md
│   ├── PLAN DE MANTENIMIENTO 2026 - LGR - CNRT v3.xlsx
│   └── legacy_bd/    # Fuentes de datos legacy (archivos de prueba)
└── context/          # Reglas de negocio y particularidades (.md) (pendiente)


### Fuentes de Datos Legacy

ARS_MP/
├── docs/
│   ├── maintenance_cycle.md  # Ciclos de mantenimiento por flota
│   └── legacy_bd/
│       ├── Accdb/
│       │   ├── CSR_Kms_MantEvents.xlsx
│       │   ├── CSR_LecturasKms.csv
│       │   ├── CSR_MantEvents.csv
│       │   ├── CSR_Modulos.csv
│       │   └── DB_CCEE_Programación 1.1.accdb
│       └── Access20/
│           ├── baseCCEE.mdb
│           ├── baseCCRR.mdb
│           └── baseLocs.mdb
└── context/          # Reglas de negocio y particularidades (.md)

- **Access .mdb (VB6)**: Sistema actual Legacy Since 1990
- **Access .accdb**: Sistema actual 2015-presente
- **CSV/Excel**: Reportes manuales de talleres
- **Sistema PHP/Laravel**: Futuro punto de integración (sin acceso actual)

---

## ✅ Checklist de Inicio

Antes de comenzar, verificar:

- [ ] Python 3.11+ instalado
- [ ] PostgreSQL 15+ funcionando
- [ ] Entorno virtual creado: `python -m venv .venv`
- [ ] Dependencias base: `pip install django pandas openpyxl pytest`
- [ ] Docker Desktop (opcional pero recomendado)
- [ ] Acceso a archivos .mdb/.accdb de prueba
- [ ] Carpeta `C:\Programmes\TFM\ARS_MP` creada

---

