## 🚀 3 - Leer BD legacy (Microsoft Access) (prompt para IA)

### Objetivo

Inspeccionar las bases de datos legacy **Microsoft Access** (`.accdb` y `.mdb`) incluidas en el repo y obtener, en **modo solo lectura**, un inventario completo de:

- Tablas (nombres y tipo)
- Consultas guardadas (queries/views, si el driver las expone)
- Columnas (tipo, nulabilidad, tamaño, default cuando esté disponible)
- Claves primarias y candidatas (si se puede inferir)
- Índices (columnas, uniqueness)
- Relaciones / foreign keys (si el driver las expone)

Además, exportar esos metadatos a archivos dentro de `docs/` para poder usarlos en el diseño del modelo y del ETL.

### Contexto

- Proyecto: `ARS_MP`
- SO/Shell: Windows + **PowerShell 7 (`pwsh`)**
- Bases legacy disponibles en el repo:
	- `docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1.accdb`
	- `docs/legacy_bd/Access20/baseCCEE.mdb`
	- `docs/legacy_bd/Access20/baseCCRR.mdb`
	- `docs/legacy_bd/Access20/baseLocs.mdb`

Convenciones del proyecto (según `AGENTS.md`):

- Responder en español.
- Código en inglés (nombres de funciones/variables).
- Documentación técnica en inglés en `docs/`.
- Reglas/criterios de negocio en español en `context/`.
- No modificar fuentes legacy: abrir SIEMPRE read-only.

### Instrucciones para la IA

Actuá como developer senior. Usá comandos compatibles con **PowerShell 7** (no bash). Priorizá una solución que funcione en Windows sin depender de herramientas de Linux.

#### 1) Verificar prerequisitos (ODBC + Python)

1) Validar que estamos parados en la raíz del repo:

```powershell
Set-Location "C:\Programmes\TFM\ARS_MP"
```

2) Confirmar Python disponible:

```powershell
python --version
```

3) Confirmar que existe el driver ODBC de Access.

Vamos a consultar drivers desde Python (más confiable que el panel de Windows):

```powershell
python -c "import pyodbc; print('\n'.join(pyodbc.drivers()))"
```

Si este comando falla porque falta `pyodbc`, instalarlo:

```powershell
python -m pip install pyodbc
python -c "import pyodbc; print('\n'.join(pyodbc.drivers()))"
```

Drivers esperados (uno de estos suele existir):

- `Microsoft Access Driver (*.mdb, *.accdb)`
- `Microsoft Access Driver (*.mdb)`

Si NO hay ningún driver de Access, explicar el bloqueo y proponer instalar **Microsoft Access Database Engine** (ACE) correspondiente a la arquitectura (x64 recomendado) y volver a intentar.

#### 2) Script de introspección (solo lectura)

Crear un script Python en `etl/extractors/access_introspect.py` que:

- Use `pyodbc`.
- Se conecte a cada DB con `ReadOnly=1`.
- Genere salidas en `docs/legacy_bd/introspection/<db_name>/`:
	- `tables.csv`
	- `columns.csv`
	- `indexes.csv` (si se puede)
	- `relationships.csv` (si se puede)
	- `queries.csv` (si se puede)
	- `summary.md` (resumen humano en inglés, porque va en `docs/`)

Requisitos del script:

- Type hints + docstrings estilo Google.
- Nombres en inglés.
- Manejo explícito de errores: si una DB no se puede abrir, el script continúa con las otras y reporta el error.
- No leer datos completos de tablas (solo metadata), para que sea rápido.

Pistas técnicas (ODBC):

- Listar tablas:
	- `cursor.tables(tableType='TABLE')`
	- También considerar `tableType='VIEW'` si el driver lo expone.
- Listar columnas:
	- `cursor.columns(table='<name>')`
- Índices/estadísticas (puede ser limitado en Access):
	- `cursor.statistics(table='<name>', unique=False)`
	- `cursor.statistics(table='<name>', unique=True)`
- Relaciones (puede no estar soportado por el driver):
	- `cursor.foreignKeys(table='<name>')`

El script debe registrar qué partes no están disponibles por limitaciones del driver.

#### 3) Ejecutar introspección sobre las DB del repo

Ejecutar el script sobre las cuatro DB:

```powershell
python -m etl.extractors.access_introspect \
	--db "docs\legacy_bd\Accdb\DB_CCEE_Programación 1.1.accdb" \
	--db "docs\legacy_bd\Access20\baseCCEE.mdb" \
	--db "docs\legacy_bd\Access20\baseCCRR.mdb" \
	--db "docs\legacy_bd\Access20\baseLocs.mdb" \
	--out "docs\legacy_bd\introspection"
```

Nota: la ruta contiene espacios y acentos; usar siempre comillas.

#### 4) Entregables y verificación

Al finalizar, verificar que se generaron carpetas por DB y que hay un resumen:

```powershell
Get-ChildItem "docs\legacy_bd\introspection" -Recurse | Select-Object FullName
```

La salida mínima esperada:

- `docs/legacy_bd/introspection/DB_CCEE_Programación 1.1/summary.md`
- `docs/legacy_bd/introspection/baseCCEE/summary.md`
- `docs/legacy_bd/introspection/baseCCRR/summary.md`
- `docs/legacy_bd/introspection/baseLocs/summary.md`

#### 5) (Opcional) Documento técnico de hallazgos

Crear un documento técnico en inglés en `docs/legacy_bd/access_schema_overview.md` con:

- Qué DBs existen y para qué parecen servir.
- Tablas principales y sus claves.
- Observaciones de calidad: campos con nombres inconsistentes, tipos raros, fechas/ids, posibles llaves compuestas.
- Limitaciones encontradas (ej. el driver no expone queries o FKs).

### Restricciones

- NO modificar ninguna base `.mdb/.accdb`.
- NO volcar datos completos; solo metadata.
- NO agregar secretos.
