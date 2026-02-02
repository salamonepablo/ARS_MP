## 🚀 4 - Estructura de las Unidades de Mantenimiento (prompt para IA)

### Objetivo

Definir la estructura de la flota de material rodante de la **Línea Roca** (unidades eléctricas, diésel y remolcadas) y, en particular, describir cómo se componen las **unidades eléctricas** (módulos) a nivel de coches.

#### Inventario (alto nivel)

- 86 Módulos CSR (CRRC) eléctricos.
- 25 Módulos Toshiba eléctricos.
- 24 Locomotoras diésel.
	- 9 Locomotoras CNR (origen China).
	- 15 Locomotoras GM-EMD (origen USA).
- 2 Coches Motores diésel Nohab (origen Portugal) (servicio tren universitario).
- 59 Coches remolcados Materfer (pasajeros servicio local y cercanías).
- 90 Coches remolcados CNR (pasajeros servicio larga distancia).

#### Alcance inicial (primera etapa)

En primera instancia vamos a trabajar solamente con el **material rodante eléctrico** (Módulos CSR y Módulos Toshiba), usando la base de datos legacy **Microsoft Access** (`.accdb`) donde toda la información se encuentra en:

- `DB_CCEE_Programación 1.1.accdb`

#### Estructura de módulos CSR (CCEE)

Los módulos CCEE CSR están armados en **triplas** y en **cuádruplas**, compuestos de la siguiente forma:

- **Módulo CSR (3 coches)**: Coche motriz 1 "MC1" en bbdd + Coche remolque "R" R1 en bbdd + Coche motriz 2 "MC2" en bbdd
- **Módulo CSR (4 coches)**: Coche motriz 1 "MC1" en bbdd + Coche remolque "R1" en bbdd + Coche remolque "Prima" "R2" en bbdd + Coche motriz 2 "MC2" en bbdd

La flota se compone de **86 Módulos CSR**:

- 42 Módulos cuádruplas.
- 44 Módulos triplas.

Regla de numeración:

- Los módulos **1 a 42** son cuádruplas.
- Los módulos **43 a 86** son triplas.

Formaciones:

- Con **1 tripla + 1 cuádrupla** se arman formaciones de **7 coches**.

#### Estructura de módulos Toshiba

La flota Toshiba se compone de:

- 13 Módulos de **3 coches**: (M "MC1" en bbdd + R "R1" en bbdd + M "MC2" en bbdd)
- 13 Módulos de **3 coches**: (M "MC1" en bbdd + R "R1" en bbdd + M "MC2" en bbdd)
- 12 Módulos de **4 coches**: (M "MC1" en bbdd + R "R1" en bbdd + R' "RP" en bbdd + M "MC2" en bbdd)

Formaciones:

- También se arman formaciones de **7 coches** con **2 módulos** (1 tripla + 1 cuádrupla).

### Contexto

- Proyecto: `ARS_MP`
- SO/Shell: Windows + **PowerShell 7 (`pwsh`)**
- Bases legacy disponibles en el repo:
	- `docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1.accdb`
	- `docs/legacy_bd/Access20/baseCCEE.mdb` **Base de Módulos CSR y Toshiba** que tiene la misma información que la `.accdb` pero en formato más antiguo. para un SW desarrollado en VB6. (Se usa actualmente para generación de informes y reportes de mantenimiento)
	- `docs/legacy_bd/Access20/baseCCRR.mdb` **Base de Coches Remolcados CNR y Materfer** para mantenimiento de coches remolcados.
	- `docs/legacy_bd/Access20/baseLocs.mdb` **Base de Locomotoras** para mantenimiento de locomotoras diésel y se incluyen en ésta base los coches motores Nohab.

Convenciones del proyecto (según `AGENTS.md`):

- Responder en español.
- Código en inglés (nombres de funciones/variables).
- Documentación técnica en inglés en `docs/`.
- Reglas/criterios de negocio en español en `context/`.
- `core/` no depende de Django ni infraestructura.
- No modificar fuentes legacy: abrir SIEMPRE read-only.

### Instrucciones para la IA

Actuá como developer senior. Usá comandos compatibles con **PowerShell 7** (no bash). Priorizá claridad y consistencia de términos (módulo, coche, tripla/cuádrupla, formación).


### Restricciones

- NO modificar ninguna base `.mdb/.accdb`.
- NO volcar datos completos; solo metadata.
- NO agregar secretos.