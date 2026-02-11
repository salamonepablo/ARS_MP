## 🚆 Ciclos de Mantenimiento Ferroviario

En el mantenimiento de material rodante ferroviario, los **ciclos de mantenimiento** son períodos predefinidos en los que se realizan intervenciones para asegurar la **operatividad** y la **seguridad** de las unidades.

### 📏 ¿Cómo se mide un ciclo?

- 🧮 **Kilometraje acumulado**: intervenciones cada $X$ km.
- 📅 **Tiempo calendario**: “lo que ocurra primero” respecto a km.
- 🧩 **Ciclos especiales por componente**: p. ej. motores diésel / compresores por horas de uso.

> Nota: en la práctica, el vencimiento suele evaluarse por el criterio más restrictivo (km o tiempo).

---

## 🔧 Tipos de Intervenciones

### ⚡ Flota CSR (Módulos de coches eléctricos)

#### 🟢 Revisiones periódicas / livianas / menores / de depósito

| Código | Intervención | Frecuencia (km) | Frecuencia (tiempo) |
|---|---|---:|---:|
| IQ | Inspección Quincenal | 6.250 | 15 días |
| IB | Inspección Bimestral | 25.000 | 60 días |
| AN | Revisión Anual | 187.500 | 15 meses |
| BA | Revisión Bianual | 375.000 | 2,5 años |

#### 🟠 Revisiones pesadas / mayores / de taller

| Código | Intervención | Frecuencia (km) | Frecuencia (tiempo) |
|---|---|---:|---:|
| RS / PE | Reparación Pentanual / Intervención de Separación | 750.000 | 5 años |
| DA / RG | Reparación Decanual / Reparación General | 1.500.000 | 10 años |

---

### ⚡ Flota Toshiba (Módulos de coches eléctricos)

#### 🟢 Revisiones periódicas / livianas / menores / de depósito

| Código | Intervención | Frecuencia (km) | Frecuencia (tiempo) |
|---|---|---:|---:|
| MEN | Inspección Mensual | 30.000 | — |

#### 🟠 Revisiones pesadas / mayores / de taller

| Código | Intervención | Frecuencia (km) | Frecuencia (tiempo) |
|---|---|---:|---:|
| RB | Reparación Bienal | 300.000 | — |
| RG | Reparación General | 600.000 | — |

---

## 🔺 Jerarquía de Intervenciones (Herencia/Pisado)

Un concepto clave del mantenimiento ferroviario es que **las intervenciones mayores "pisan" (resetean) a las menores**. Cuando se realiza una intervención de mayor jerarquía, todas las intervenciones de menor jerarquía heredan esa fecha y kilometraje como su nuevo punto de partida.

### Regla de Pisado

> Cuando una intervención de nivel superior se ejecuta, **todas las intervenciones de niveles inferiores resetean su conteo** (fecha y km) al momento de esa intervención mayor.

### ⚡ Jerarquía CSR (de mayor a menor)

```
DA (Decanual) → PE (Pentanual) → BA (Bianual) → AN (Anual) → IB (Bimestral) → IQ (Quincenal)
```

**Ejemplo:** Si se realiza una DA el 01/01/2026 a 1.500.000 km:
- PE, BA, AN, IB, IQ → todos pasan a tener última fecha 01/01/2026 y km base 1.500.000

### ⚡ Jerarquía Toshiba (de mayor a menor)

```
RG (Reparación General) → RB (Bienal) → MEN (Mensual)
```

**Ejemplo:** Si se realiza una RG el 14/10/2025 a 5.468.568 km:
- RB y MEN → pasan a tener última fecha 14/10/2025 y km base 5.468.568
- El conteo de km para RB y MEN arranca desde 0 a partir de ese momento

### 📊 Implicaciones para la Proyección

1. **Próxima Intervención**: Se calcula considerando TODOS los ciclos y cuál vence primero
2. **KM desde última intervención**: Para cada ciclo, se usa la fecha/km de ESE ciclo O de uno superior si fue más reciente
3. **% de ciclo**: Se calcula contra el ciclo correspondiente (ej: RB = 300.000 km, MEN = 30.000 km)

### Ejemplo Práctico: T09 (Toshiba)

- **RG realizada**: 14/10/2025 a 5.468.568 km
- **KM actual**: 5.490.502 km
- **KM desde RG**: 21.934 km

| Intervención | Ciclo (km) | Última Fecha | KM Base | KM desde entonces | % Ciclo |
|--------------|------------|--------------|---------|-------------------|---------|
| MEN | 30.000 | 14/10/2025* | 5.468.568 | 21.934 | 73% |
| RB | 300.000 | 14/10/2025* | 5.468.568 | 21.934 | 7% |
| RG | 600.000 | 14/10/2025 | 5.468.568 | 21.934 | 4% |

*Heredado de RG (pisado)

**Próxima Intervención**: MEN (faltan ~8.066 km para los 30.000)