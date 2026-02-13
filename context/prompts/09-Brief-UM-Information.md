## 🚀 9 - Brief UM (Unidad de Mantenimiento) + Reglas de Cálculo (prompt para IA)

### Objetivo

Dejar por escrito (en español y de forma no ambigua) qué es una **UM (Unidad de Mantenimiento)** en este proyecto y cuáles son las **reglas mínimas de cálculo** para:

- Kilometrajes (total, mes actual, promedios)
- Último mantenimiento válido
- Vencimientos por ciclo (km / tiempo; “lo que ocurra primero” cuando aplique)

Este brief sirve como base para el prompt 10 (proyección) y para implementar lógica en `core/` sin depender de Django.

### Alcance (MVP)

- Solo flota eléctrica Línea Roca: **CSR + Toshiba**.
- UM principal: **EMU/Módulo** (CSR `M01..M86` y Toshiba `T01..T25`).
- Locomotoras y coches remolcados: fuera de alcance.

### Contexto / Fuentes

- Reglas de ciclos: `docs/maintenance_cycle.md`
- Identificación de flota: `docs/rolling_stock_fleet.md`
- Datos operativos (principal): Access `DB_CCEE_Programación 1.1_old.accdb`
- Datos complementarios (si aplica): `docs/legacy_bd/Accdb/URG-Modulos.csv`
- Tablas/queries típicas mencionadas en prompts previos:
	- `A_00_Kilometrajes` (lecturas de km)
	- `A_00_OT_Simaf` (órdenes / tareas)
	- `A_00_Formaciones` / `A_14_Estado_Formaciones_Consulta` (composición/estado)

### Definiciones

#### UM (Unidad de Mantenimiento)

Para el MVP, una UM es un **módulo eléctrico**:

- CSR: `M01` a `M86`
- Toshiba: `T01` a `T25`

La UM se usa para mostrar cards (fleet) y para proyectar mantenimiento.

#### “Último mantenimiento”

Se define como la **última OT válida** según:

- Pertenece a la UM.
- Tiene fecha (y si hay varias el mismo día, tomar la más reciente por orden/ID).
- Su tipo/tarea puede mapearse a un ciclo definido en `docs/maintenance_cycle.md`.

Si una OT no corresponde a ningún ciclo del documento, **no debe considerarse** para “último mantenimiento” de ciclos.

### Reglas de mapeo de tareas (OT → ciclo)

El contenido de OT suele venir con sufijos/variantes (ej. `IQ1`, `IQ2`, `IQ3`).

- Regla base: normalizar tomando el prefijo alfabético (ej. `IQ3` → `IQ`, `AN2` → `AN`).
- Para CSR, ciclos esperados: `IQ`, `IB`, `AN`, `BA`, `RS`/`PE`, `DA`/`RG`.
- Para Toshiba, ciclos esperados: `MEN`, `RB`, `RG`.

Nota: si aparece `RG` en CSR o `DA` en Toshiba, tratarlo como dato inconsistente y documentarlo (no inventar reglas sin confirmación).

### Reglas de kilometraje

#### Km total acumulado

- Base: tomar el valor máximo disponible en `A_00_Kilometrajes` para la UM.
- Si existen distintos “contadores” (por ejemplo por evento), elegir el contador oficial utilizado en los reportes del legacy (documentar cuál y por qué).

#### Km del mes actual

- Definición: diferencia entre “km acumulado mes actual” y “km acumulado mes anterior”.
- Si falta el mes anterior, dejar `0` y registrar warning (no romper la UI).

#### Km desde último mantenimiento

- Se calcula, no se guarda:
	- `km_since_maintenance = km_total_accumulated - km_at_last_maintenance`

Donde `km_at_last_maintenance` se obtiene del registro más cercano al evento/fecha del último mantenimiento (según cómo esté modelado en la base; documentar la aproximación).

### Reglas de vencimiento por ciclo (base conceptual)

Para un ciclo $c$:

- Vencimiento por km: cuando `km_since_last_c >= km_threshold_c`
- Vencimiento por tiempo: cuando `days_since_last_c >= days_threshold_c`
- Si el ciclo tiene ambos (CSR): vence por el que ocurra primero.
- Si el ciclo no tiene tiempo (Toshiba en `maintenance_cycle.md`): vence solo por km.

### Entregables

1) Documento de negocio (español) en `context/` con:

- Definición de UM para el MVP.
- Mapeo OT→ciclo.
- Reglas de cálculo de km y selección de último mantenimiento.

2) Documento técnico (inglés) en `docs/` con:

- Cómo se transforman los datos del legacy en un “snapshot” usable por `core/`.
- Supuestos explícitos y qué se hace ante datos faltantes/inconsistentes.

### Restricciones

- NO modificar fuentes legacy `.mdb/.accdb`.
- NO inventar reglas si hay ambigüedad: documentar supuestos y dejar TODO claro.
- `core/` no depende de Django.