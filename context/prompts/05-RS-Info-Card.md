## 🚀 5 - Cards de módulos (UI) (prompt para IA)

### Objetivo

Implementar una vista web (Django) en formato **cards** con **Tailwind CSS** para mostrar la información de cada módulo de la flota de material rodante **eléctrico** de la **Línea Roca**:

- 86 módulos **CSR**
- 25 módulos **Toshiba**

Total: **111 cards** (una por módulo).

La UI debe verse similar a la imagen adjunta y/o reutilizar el layout ya realizado en el proyecto anterior:

- Referencia (proyecto anterior): `C:\Programmes\maintenance_projection\`

![Referencia UI](image.png)

### Alcance funcional

#### Resumen (encabezado / KPIs)

- Total de km recorridos en el **mes actual**:
	- Total CSR
	- Total Toshiba
	- Total general (CSR + Toshiba)

#### Cards (una por módulo)

Cada card debe mostrar, como mínimo:

- Tipo de módulo: CSR o Toshiba
- Número de módulo
- Kilometraje recorrido en el mes actual
- Kilometraje total acumulado
- Fecha del último mantenimiento
- Kilometraje desde el último mantenimiento
- Días desde el último mantenimiento

### Contexto

- Proyecto: `ARS_MP`
- SO/Shell: Windows + **PowerShell 7 (`pwsh`)**
- Stack UI: Django Templates + HTMX + Alpine.js + Tailwind CSS
- Referencia de diseño/código existente:
	- `C:\Programmes\maintenance_projection\` (tomar componentes/plantillas como base si existen)

Convenciones del proyecto (según `AGENTS.md`):

- Responder en español.
- Código en inglés (nombres de funciones/variables).
- Documentación técnica en inglés en `docs/`.
- Reglas/criterios de negocio en español en `context/`.
- `core/` no depende de Django.

### Instrucciones para la IA

Actuá como developer senior. Buscá una solución pragmática que permita obtener un resultado visual similar a la imagen.

#### 1) Instalación de dependencias

Instalá lo mínimo necesario para lograr Tailwind + interactividad ligera.

Opción recomendada (setup “bien” para Django):

- Integrar Tailwind con Django (p. ej. `django-tailwind`) y usar Node.js para build.
- Agregar dependencias Python/UI que falten para HTMX/Alpine (si se usan por CDN, no requieren instalación).

Opción rápida (MVP visual):

- Usar Tailwind vía CDN en la plantilla base para obtener el look & feel rápido.
- HTMX y Alpine también vía CDN.

En ambos casos, dejar el proyecto listo para correr en desarrollo.

#### 2) Reutilización desde proyecto anterior

Si en `C:\Programmes\maintenance_projection\` ya existe una vista similar:

- Identificá templates/componentes reutilizables.
- Copiá el enfoque de layout (grid, cards, badges, tipografías, colores) y adaptalo al repo actual.

#### 3) Implementación de la vista

- Crear una vista y template que renderice **111 cards**.
- Usar un layout responsive:
	- 1 columna en mobile
	- 2-3 en tablet
	- 4+ en desktop (según ancho)
- Cada card debe tener jerarquía visual clara (título, números grandes, subtítulos y “labels”).

Generar un **dataset stub** en memoria (lista de módulos CSR 1–86 y Toshiba 1–25 con valores mock) para poder construir la UI primero.

#### 4) Entregables esperados

- Página accesible desde una URL clara (por ejemplo `/fleet/modules/`).
- Template con Tailwind que replique el estilo de la imagen (cards + métricas arriba).
- Instrucciones en el README (o nota corta en `docs/`) para correr en dev.

### Fuera de alcance (por ahora)

- Locomotoras diésel, coches remolcados y demás flota no eléctrica (solo CSR + Toshiba en esta etapa).

### Restricciones

- NO agregar secretos.
- NO modificar fuentes legacy `.mdb/.accdb`.
- No volcar datos completos; si se usan datos reales, limitarse a lo mínimo necesario para la UI.

