## 🚀 10 - Proyección de mantenimiento (grilla tipo Excel) (prompt para IA)

### Objetivo

Implementar la vista core de proyección: una **grilla tipo Excel** para proyectar, mes a mes, el kilometraje de cada módulo por cada tipo de intervención pesada, visualizar umbrales (semáforo por color) y permitir exportación a Excel respetando el formato.

Referencia visual:

![Capture40](Capture40.png)

### Alcance funcional

#### 1) Estructura de la grilla

- Una fila por cada módulo de la flota.
- Para cada módulo, una fila por cada tipo de intervención pesada.
- Columnas para el mes actual y los meses siguientes.
	- Cantidad de meses dinámica.
	- Valor inicial: **18 meses**.

#### 2) Parámetros (inputs)

- Textbox: cantidad de meses a proyectar.
	- Default: **18**.
- Textbox: km promedio mensual flota CSR.
	- Default: **12.000 km**.
- Textbox: km promedio mensual flota Toshiba.
	- Default: **8.000 km**.

Estos defaults deben definirse en constantes donde corresponda.

#### 3) Acciones / controles

- Control para elegir la flota a proyectar (2 botones o equivalente).
- Botón: **Generar Proyección**.
- Botón: **Exportar a Excel**.

#### 4) Proyección y semáforo (formato)

- Partir del dato actual del detalle del módulo.
- Proyectar hacia adelante sumando mes a mes el promedio mensual.
	- Tener en cuenta que hoy tenemos datos hasta esta altura del mes: para el mes siguiente se suma el promedio mensual completo, pero para el mes actual se proyecta solo lo que resta del mes.
	- Cálculo sugerido (aprox.): `km_restante_mes = (km_promedio_mensual / 30) * dias_restantes_del_mes`.
- Cuando el valor supere el umbral, mostrar el número de km y marcar el semáforo (en vez del estilo por defecto sin fondo y con texto negro).

Ejemplo de colores (según la referencia)

Flota CSR:
- Anual (AN): fondo verde suave + texto verde más oscuro.
- Bianual (BA): fondo amarillo suave + texto amarillo más oscuro.
- Pentanual (PA): fondo celeste suave + texto azul/celeste más oscuro.
- Decanual (DA): fondo rojo suave + texto rojo más oscuro.

Flota Toshiba:
- Bienal (RB): fondo amarillo suave + texto amarillo más oscuro.
- General (RG): fondo rojo suave + texto rojo más oscuro.

#### 5) Interacción: edición de celdas (marcar intervención)

En la celda que el usuario decida, haciendo doble click se colocará automáticamente un texto que será el que corresponde a la fila/tipo (AN, BA, PA, DA). Al volver a hacer doble click, debe volver al valor anterior de km.

Efecto al hacer doble click (jerarquía/herencia):

- Resetear los km de esa fila y de sus "herederas".
- En las herederas, en el mes marcado, colocar el valor **"0"**.
- A partir del mes siguiente, en esas filas (pentanual y herederas) se verá el km promedio acumulándose mes a mes, sin formato (dentro de ciclo).
- En este ejemplo, la **Decanual** (superior) sigue acumulando mes a mes hasta superar su umbral (rojo) o hasta que el usuario haga click y coloque **"DA"** y se reseteen las inferiores.

#### 6) Exportación a Excel

- La exportación debe respetar el formato de colores.
- La exportación debe respetar los valores escritos por el usuario.

### Contexto

- Proyecto: `ARS_MP`
- SO/Shell: Windows + **PowerShell 7 (`pwsh`)**
- UI: Django Templates + HTMX + Alpine.js + Tailwind CSS

Convenciones del proyecto (según `AGENTS.md`):

- Responder en español.
- Código en inglés (nombres de funciones/variables).
- Documentación técnica en inglés en `docs/`.
- Reglas/criterios de negocio en español en `context/`.
- `core/` no depende de Django.

### Instrucciones para la IA

Actuá como developer senior. Priorizá una implementación incremental que permita ver la grilla funcionando lo antes posible.

- Si todavía no hay datos reales listos, arrancar con un dataset stub/mocks para construir la UI y la lógica de proyección.
- Mantener el formato visual lo más cercano posible a la imagen de referencia.

### Entregables esperados

- Vista accesible desde una URL clara.
- Grilla generada según flota, meses y promedios.
- Semáforo por tipo de intervención.
- Interacción mínima: doble click para alternar entre km y sigla (AN/BA/PA/DA), con reseteo/herencia según corresponda.
- Exportación a Excel con formato y valores.

### Restricciones

- DDD.
- Principios SOLID.
- Arquitectura Clean.
- NO escribir sobre base legacy: solo lectura, siempre.

