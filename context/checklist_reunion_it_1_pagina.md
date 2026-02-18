# ARS_MP · Checklist de 1 página para reunión con IT

> Uso: imprimir y completar en reunión (máximo 30 minutos).

## 1) Decisión rápida de despliegue

- [ ] **Opción A (preferida):** servidor corporativo interno (on-prem / VM).
- [ ] **Opción B (piloto):** cloud externo con URL pública (free-tier/trial).
- [ ] Responsable técnico definido: ____________________
- [ ] Fecha objetivo de piloto: ____ / ____ / ______

## 2) Mínimos técnicos (Go / No-Go)

- [ ] Python 3.11+ disponible para la app.
- [ ] PostgreSQL 15+ disponible (nueva o existente).
- [ ] Conectividad app ↔ DB validada.
- [ ] URL accesible para usuarios (interna o externa).
- [ ] HTTPS y política de credenciales/secretos definida.

## 3) Si se evalúa cloud externo (free-tier)

- [ ] IT permite **allowlist por dominio** en proxy corporativo.
- [ ] Compliance confirma que los datos pueden alojarse fuera de la empresa.
- [ ] Legal/compras confirma si hace falta DPA/contrato.
- [ ] Se acepta que free-tier **no tiene SLA** y puede tener suspensión por inactividad.

## 4) Operación mínima para piloto

- [ ] Responsable de despliegues y reinicios: ____________________
- [ ] Backup de base de datos definido (frecuencia): ______________
- [ ] Monitoreo/logs mínimos definidos.
- [ ] Criterio de escalado definido (pasar a plan pago o mover a infraestructura corporativa).

## 5) Entregables para cerrar la reunión

- [ ] Entorno elegido (A o B) y justificación.
- [ ] Puertos/dominios aprobados por IT.
- [ ] Dueño de operación + plan de soporte.
- [ ] Fecha de inicio de piloto y fecha de revisión.

---

## Decisión final (marcar una)

- [ ] **GO**: se inicia piloto con condiciones acordadas.
- [ ] **GO con riesgo**: faltan aprobaciones puntuales (detallar abajo).
- [ ] **NO-GO**: bloquear hasta resolver compliance/infraestructura.

Riesgos/pendientes:
- ________________________________________________________________
- ________________________________________________________________

