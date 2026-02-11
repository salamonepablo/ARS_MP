# Grilla de Proyeccion de Mantenimiento

## Descripcion

La grilla de proyeccion es la herramienta principal para planificar el
mantenimiento pesado de la flota. Muestra, mes a mes, cuantos km lleva
acumulados cada modulo desde su ultima intervencion de cada tipo.

## Acceso

Desde la vista de flota (`/fleet/modules/`), boton **"Man. Planner"**.

URL: `/fleet/planner/?fleet=csr` o `/fleet/planner/?fleet=toshiba`

## Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| Flota | CSR | CSR o Toshiba |
| Meses | 18 | Cantidad de meses a proyectar (1-60) |
| KM Prom. Mensual | CSR: 12.000, Toshiba: 8.000 | Promedio mensual para proyectar |

## Semaforo de colores

Cuando los km acumulados superan el umbral del ciclo, la celda se colorea:

### Flota CSR
- **AN (Anual)**: Verde - Umbral 187.500 km
- **BA (Bianual)**: Amarillo - Umbral 375.000 km
- **PE (Pentanual)**: Celeste - Umbral 750.000 km
- **DA (Decanual)**: Rojo - Umbral 1.500.000 km

### Flota Toshiba
- **RB (Bienal)**: Amarillo - Umbral 300.000 km
- **RG (Reparacion General)**: Rojo - Umbral 600.000 km

## Interaccion: Marcar intervenciones

**Doble click** en una celda coloca la sigla del ciclo (ej: "AN") y
resetea los km de las filas herederas a 0 en ese mes.

Ejemplo: si hago doble click en la celda de **PE** del mes de Junio:
- PE: muestra "PE" en esa celda
- BA: se pone en 0 en Junio, y a partir de Julio acumula desde 0
- AN: se pone en 0 en Junio, y a partir de Julio acumula desde 0

Hacer doble click de nuevo revierte al valor original.

## Prorateo del mes actual

El mes actual no suma el promedio completo, sino proporcional a los
dias restantes:

```
km_restante_mes = (km_promedio_mensual / dias_del_mes) * dias_restantes
```

## Exportacion

Boton **"Exportar a Excel"** genera un archivo .xlsx con:
- Mismos colores del semaforo
- Formato numerico con separador de miles
- Columnas fijas (modulo, ciclo, umbral)
