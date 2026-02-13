## 🚀 8 - Conectar a la base legacy (.accdb) y reemplazar `stub_data` (prompt para IA)

### Objetivo

Reemplazar el dataset mock actual (en `web/fleet/stub_data.py`) por lectura real desde la base legacy **Microsoft Access** (`.accdb`) protegida con contraseña. Corroborar la integridad de los datos (ej: cantidad de módulos) con la fuente original (CSR+Toshiba).

**Password de la base (secreto)**: `1041` (debe ir en `.env`, nunca hardcodeado, nunca commiteado).

### Campos de la Card (Tarjeta del Módulo)

Cada card debe mostrar la siguiente información:

#### 1. Número de Módulo
- **Display principal**: Número del módulo (ej: `01`)
- **Display secundario**: "Módulo 01" y debajo la composición de coches
- **Ejemplo**: `MC1 5001 - R1 5601 - R2 5801 - MC2 5002`
- **Fuente**: Ver estructura definida en `docs/rolling_stock_fleet.md`
  - **Tomar Estado de armado de mòdulos de la consulta "A_14_Estado_Formaciones_Consulta"**

#### 2. Kilometraje Total Acumulado
- **Descripción**: Km totales desde última RG (o desde puesta en marcha si no tiene RG)
- **Fuente**: Tabla `A_00_Kilometrajes` - tomar el valor máximo para el módulo
- **Nota**: Para CSR (sin RG todavía) = km total acumulado. Para Toshiba, ver punto 6.

#### 3. Kilometraje del Mes Actual
- **Descripción**: Km recorridos en el mes actual
- **Cálculo**: Diferencia entre "km acumulados mes actual" y "km acumulados mes anterior"
- **Fuente**: Tabla `A_00_Kilometrajes`

#### 4. Promedio de Kilometraje
- **Descripción**: Promedio diario de los últimos 30 días
- **Cálculo**: A definir según datos disponibles
- **Fuente**: Tabla `A_00_Kilometrajes`

#### 5. Último Mantenimiento
- **Datos a mostrar**:
  - Fecha del último mantenimiento
  - Tipo completo (ej: `IQ3`, `AN2`, etc.)
  - Km recorridos desde ese mantenimiento hasta hoy

- **Fuente**: Tabla `A_00_OT_Simaf`
  - Ordenar por fecha descendente
  - Tomar el registro más reciente
  - Usar campo "Tarea"

- **Mapeo de tipos**:
  - Inspeccionar la tabla para identificar correspondencia con `docs/maintenance_cycle.md`
  - Ejemplos: IQ1 = IQ2 = IQ3 → IQ | AN1 = AN2 → AN
  - **Regla**: Si el tipo de OT NO corresponde a ningún ciclo definido en `maintenance_cycle.md`, no mostrarlo en la card
  - Pero SÍ mostrar la fecha del último mantenimiento registrado que coincida con el ciclo

- **Caso sin OT**:
  - Mostrar: `"Sin OT registrada"`
  - Tomar kilometraje desde última RG o fecha de puesta en servicio

#### 6. Fecha de Referencia (RG / Puesta en Servicio)
- **CSR**: No tienen RG todavía → km desde puesta en marcha = km total acumulado
- **Toshiba**: Tienen RG pero no todas están en la base legacy
- **Fuente complementaria**: CSV en `docs/legacy_bd/Accdb/URG-Modulos.csv`
  - Columnas: número de módulo, fecha de puesta en servicio (CSR), fecha última RG (Toshiba)

#### Resumen de fuentes de datos
- **Principal**: `docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1_old.accdb`
- **Complementaria**: `docs/legacy_bd/Accdb/URG-Modulos.csv`
- **Introspección**: `docs/legacy_bd/introspection/DB_CCEE_Programación 1.1/`

**Importante**: No traer tablas completas, solo los campos necesarios para la vista. 


- Fuente principal (MVP): `docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1_old.accdb` + 'c:\Programmes\TFM\ARS_MP\docs\legacy_bd\Accdb\URG-Modulos.csv'

- Referencia (proyecto anterior): `C:\Programmes\maintenance_projection\`

### Alcance (MVP)

- Solo flota eléctrica: **CSR + Toshiba**.
- Mantener la UI existente (cards) pero con datos reales.
- Si la conexión no está disponible (driver faltante / variables no definidas), permitir fallback controlado a stub con un mensaje claro en logs.


### Contexto

- Proyecto: `ARS_MP` - Título "Argentinian Rolling Stock Maintenance Planner"
- SO/Shell: Windows + **PowerShell 7 (`pwsh`)**
- Stack UI: Django Templates + HTMX + Alpine.js + Tailwind CSS
- Dependencias ya previstas en el proyecto: `pyodbc`, `python-dotenv` (ver `requirements.txt`)

Convenciones del proyecto (según `AGENTS.md`):

- Responder en español.
- Código en inglés (nombres de funciones/variables).
- TDD pragmático: tests para lógica crítica; no romper la UI.
- Documentación técnica en inglés en `docs/`.
- Reglas/criterios de negocio en español en `context/`.
- `core/` no depende de Django ni infraestructura.
- NO modificar fuentes legacy: abrir SIEMPRE read-only.

### Variables de entorno (.env)

Agregar/usar estas variables (nombres sugeridos; si ya existen, respetar los existentes):

- `LEGACY_ACCESS_DB_PATH`: ruta al `.accdb`.
- `LEGACY_ACCESS_DB_PASSWORD`: contraseña (`1041`).
- (Opcional) `LEGACY_ACCESS_ODBC_DRIVER`: por defecto `Microsoft Access Driver (*.mdb, *.accdb)`.

Ejemplo `.env` local (NO commitear):

```env
LEGACY_ACCESS_DB_PATH=docs\\legacy_bd\\Accdb\\DB_CCEE_Programación 1.1_old.accdb
LEGACY_ACCESS_DB_PASSWORD=1041
LEGACY_ACCESS_ODBC_DRIVER=Microsoft Access Driver (*.mdb, *.accdb)
```

Nota: las rutas en Windows pueden tener espacios y acentos; usar comillas cuando corresponda.

### Instrucciones para la IA

Actuá como developer senior. Usá comandos compatibles con **PowerShell 7** (no bash). Priorizá una solución pragmática, local y open-source (sin servicios pagos/cloud).

#### 1) Verificación de prerequisitos (ODBC Access)

1) Posicionarse en la raíz:

```powershell
Set-Location "C:\Programmes\TFM\ARS_MP"
```

2) Ver drivers ODBC disponibles desde Python:

```powershell
python -c "import pyodbc; print('\\n'.join(pyodbc.drivers()))"
```

- Driver esperado: `Microsoft Access Driver (*.mdb, *.accdb)`.
- Si no está, documentar el bloqueo y proponer instalar **Microsoft Access Database Engine (ACE)** acorde a la arquitectura (x64 recomendado), sin cambiar el repo.

#### 2) Crear Django Models e integración con entidades del dominio

**Prerequisito**: Las entidades del dominio ya están definidas en `context/prompts/07-Create-entities.md`.

**Tarea**:

1. Crear Django models en `infrastructure/database/models.py` que mapeen las entidades del dominio:
   - Implementar models para persistir las entidades en PostgreSQL
   - Mantener separación entre capa de dominio (`core/`) y capa de infraestructura
   - Usar nombres de tablas y campos descriptivos (verbose_name en español)

2. Crear Repositories en `infrastructure/database/repositories.py`:
   - Implementar el patrón Repository para aislar la lógica de persistencia
   - Los repositories deben devolver entidades del dominio (no Django models directamente)
   - Manejar la conversión entre Django models y entidades del dominio

3. Generar migraciones:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

**Principios**:
- `core/domain/` NO debe depender de Django
- Los models de Django son implementaciones concretas de las entidades
- Los repositories actúan como traducores entre capas

#### 3) Implementar conexión read-only con password

Crear una función de conexión en un lugar apropiado (ej.: `etl/extractors/access_connection.py` o `infrastructure/external/access.py`) que:

- Lea `LEGACY_ACCESS_DB_PATH`, `LEGACY_ACCESS_DB_PASSWORD` y (opcional) `LEGACY_ACCESS_ODBC_DRIVER`.
- Arme un connection string ODBC que incluya `ReadOnly=1` y la password.
- Maneje errores de forma explícita (credenciales erróneas, archivo inexistente, driver ausente).

La conexión ya está funcionando hemos probado y funciona como está

#### 4) Query mínima para alimentar las cards

Objetivo: obtener los campos necesarios para construir la estructura similar a `ModuleData`:

- Identificador/número de módulo (ver `docs/rolling_stock_fleet.md`).
- Km mes actual
  * Calcular haciendo la didferencia entre "km acumulados mes actual" y "km acumulados mes anterior" de la tabla A_00_Kilometrajes.
- Km total acumulado
  * Tomar el valor máximo de la tabla A_00_Kilometrajes para el módulo.
  
- Fecha último mantenimiento + tipo
  *  Tomar el registro más reciente de la tabla A_00_OT_Simaf correspondiente al módulo, y que sea del tipo definido en (ver `docs/maintenance_cycle.md`)
- Km al último mantenimiento (para poder calcular "km desde último mantenimiento")
  * Calcular la diferencia entre "km total acumulado" y "km acumulados al último mantenimiento". de la tabla A_00_Kilometrajes. 

Usar como guía la introspección ya generada en `docs/legacy_bd/introspection/DB_CCEE_Programación 1.1/` para identificar tablas/columnas reales.

Importante:

- No hacer full table scans innecesarios.
- Limitar el volumen de datos: traer solo lo necesario para la vista.
- Asegurar que CSR+Toshiba siguen dando **111 módulos** (o justificar diferencias con evidencia).

#### 5) Reemplazar `stub_data` sin romper la vista

Actualizar la vista `web/fleet/views.py` para que el origen de datos sea:

1) Access (si `.env` está configurado y la conexión funciona)
2) Stub (fallback) si no

Mantener estable el contrato que espera el template `web/fleet/templates/fleet/module_list.html`.

#### 6) Tests (mínimo imprescindible)

- Agregar tests que verifiquen que la vista responde (status 200) y que el fallback a stub funciona cuando no hay configuración de Access.
- No exigir que el `.accdb` exista en CI: los tests no deben depender de drivers instalados.

#### 7) Documentación técnica (en inglés)

Crear/actualizar un documento técnico en `docs/` describiendo:

- Variables de entorno usadas.
- Requisitos del driver ODBC/ACE en Windows.
- Estrategia de fallback (por qué existe y cómo se comporta).

### Entregables / Criterios de aceptación

- La URL `/fleet/modules/` renderiza las cards con datos reales cuando la conexión está configurada.
- Si falta driver/archivo/credenciales, la app sigue levantando y usa stub (con logs claros) informando del fallback.
- Tests que cubren la lógica de conexión y fallback.
- No se introducen secretos en el repo.
- No se modifica la base `.accdb`.

### Restricciones

- NO modificar fuentes legacy `.mdb/.accdb`.
- NO modificar estructura de base de datos legacy en origen.
- Dentro de las posibilidades, NO usar servicios de pago/clouds de pago.
