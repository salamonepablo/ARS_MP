# Guion de Slides — ARS_MP

> Guia para armar la presentacion en Google Slides.
> Cada seccion = 1 slide. Screenshots referenciados desde `docs/ui/`.

---

## Slide 1: Portada

- **Titulo**: ARS_MP — Argentinian Rolling Stock Maintenance Planner
- **Subtitulo**: Trabajo Final de Master — Master en Desarrollo con IA
- **Autor**: Pablo Salamone
- **Fecha**: Febrero 2026
- **Visual**: Logo Trenes Argentinos o foto de formacion electrica Linea Roca

---

## Slide 2: El problema

- Linea Roca opera **111 modulos** (86 CSR + 25 Toshiba)
- Datos de mantenimiento dispersos en:
  - Bases Access (.mdb) desde los 90
  - Access .accdb desde 2015
  - Planillas Excel manuales
  - Aplicaciones VB6
- **No hay vista unificada** para planificar mantenimiento pesado
- Las decisiones se toman con planillas manuales en Excel
- **Screenshot**: `Capture20.png` (Access legacy) y/o `Capture40.png` (la planilla Excel actual)

---

## Slide 3: La solucion — ARS_MP

- Herramienta **ETL + visualizacion web** que:
  1. Extrae datos de sistemas legacy (ODBC a Access)
  2. Normaliza en PostgreSQL (staging tables)
  3. Proyecta kilometrajes por ciclo de mantenimiento
  4. Grilla interactiva para simular intervenciones
  5. Exporta a Excel para compartir con talleres
- **Diagrama de flujo**: Access/CSV/Excel --> ETL --> PostgreSQL --> Django --> Browser/Excel

---

## Slide 4: Stack tecnologico

- Python 3.11 + Django 5 + PostgreSQL 15
- ETL: pandas, openpyxl, pyodbc
- Frontend: Django Templates + HTMX + Alpine.js + Tailwind CSS v4
- Docker Compose (PostgreSQL)
- Testing: pytest (214 tests, 97% coverage core)
- **Nota**: Mencionar que core/ es Python puro (Clean Architecture)

---

## Slide 5: Arquitectura

- Diagrama de capas:
  - `core/` — Dominio puro (sin Django)
  - `etl/` — Pipeline ETL
  - `web/` — Django (vistas + templates)
  - `infrastructure/` — DB, integraciones
- Principios: Clean Architecture, DDD, SOLID, Dependency Inversion
- Fallback graceful: si Access no esta disponible, funciona con datos stub

---

## Slide 6: Vista de flota

- 111 tarjetas con datos en tiempo real
- KM mensual, KM total, ultimo mantenimiento, dias transcurridos
- Filtrable por flota
- **Screenshot**: `Capture22.png`

---

## Slide 7: Detalle de modulo

- Informacion completa por modulo
- Tabla de ciclos pesados con barras de progreso
- Herencia de mantenimiento (jerarquia)
- **Screenshot**: `Capture30.png` o `Capture35.png`

---

## Slide 8: Maintenance Planner — La grilla

- Funcionalidad estrella del proyecto
- Filas: modulo x ciclo pesado | Columnas: meses
- Semaforo de colores cuando se supera umbral
- Doble-click para marcar intervenciones
- Reset en cascada por jerarquia de mantenimiento
- **Screenshot**: `Capture47.png` (con intervenciones marcadas)

---

## Slide 9: Jerarquia de mantenimiento

- **Regla de negocio clave**: intervencion mayor "pisa" las menores
- CSR: DA > PE > BA > AN (4 ciclos pesados)
- Toshiba: RG > RB (2 ciclos pesados)
- Ejemplo visual: si marco DA, PE/BA/AN se resetean a 0 desde ese mes
- **Screenshot**: `Capture46.png` (detalle de cascada)

---

## Slide 10: Export a Excel

- Colores identicos al browser
- Intervenciones del browser incluidas
- Filas de resumen + Control
- Listo para compartir con talleres y gerencia
- **Screenshot**: `Capture49.png` o `Capture50.png`

---

## Slide 11: Testing y calidad

- 214 tests (97% coverage en core/services)
- TDD: RED-GREEN-REFACTOR
- Tests de integracion separados (`@pytest.mark.integration`)
- Conventional Commits (26 commits)
- Documentacion: ADRs, business rules, schema introspection

---

## Slide 12: Demo en vivo (opcional)

- Si presentas en vivo: abrir `http://localhost:8000/fleet/modules/`
- Mostrar navegacion: tarjetas -> detalle -> planner -> doble-click -> export Excel
- Si no hay demo en vivo: usar los screenshots o un video grabado

---

## Slide 13: Proximos pasos

- Despliegue en nube corporativa (Railway/Render o server interno)
- Integracion con sistema Laravel corporativo (API REST)
- Dashboard con metricas agregadas
- Notificaciones de mantenimiento proximo

---

## Slide 14: Cierre

- **ARS_MP**: de planillas Excel manuales a una herramienta web interactiva
- Repositorio: `github.com/salamonepablo/ARS_MP`
- Gracias
