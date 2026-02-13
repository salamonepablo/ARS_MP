# Checklist corta para reunión con IT (despliegue ARS_MP)

> Objetivo: validar si ARS_MP puede desplegarse en infraestructura corporativa (on-prem o cloud corporativa) sin depender de Docker en puestos de usuario.

## 1) Decisión de hosting

- [ ] ¿Se puede desplegar en un **servidor interno** (VM Windows/Linux) accesible por LAN?
- [ ] Si no, ¿hay **cloud corporativa aprobada** para aplicaciones internas?
- [ ] ¿Quién será el dueño operativo del entorno (IT / área usuaria / mixto)?

## 2) Requisitos mínimos de infraestructura

- [ ] Runtime: **Python 3.11+** habilitado.
- [ ] Base de datos: **PostgreSQL 15+** disponible (instancia nueva o compartida).
- [ ] Acceso de red entre aplicación y base de datos (puerto/segmento).
- [ ] Recursos iniciales sugeridos: 2 vCPU, 4-8 GB RAM, 40+ GB disco.
- [ ] Dominio interno o URL corporativa para acceso de usuarios.

## 3) Accesos y seguridad

- [ ] ¿Se permite autenticación corporativa (AD/SSO) o quedará autenticación local de Django?
- [ ] ¿Se requiere HTTPS con certificado corporativo?
- [ ] ¿Qué puertos puede exponer la app para uso interno?
- [ ] ¿Hay restricciones para procesar archivos legacy (.mdb/.accdb/.csv/.xlsx)?
- [ ] Confirmar política de secretos: variables de entorno, credenciales y rotación.

## 4) Operación y soporte

- [ ] ¿Quién hará despliegues (IT, DevOps, equipo funcional)?
- [ ] ¿Frecuencia de backup de PostgreSQL y política de restore?
- [ ] ¿Se requiere monitoreo/logs centralizados?
- [ ] ¿Hay ventana de mantenimiento y SLA esperado?
- [ ] ¿Ambiente de prueba separado de producción?

## 5) Integraciones y datos

- [ ] ¿El servidor tendrá acceso a fuentes legacy por red/VPN?
- [ ] Si no hay acceso directo, ¿se acepta esquema de **importación por archivos**?
- [ ] ¿Formato de intercambio aprobado para carga periódica (CSV/Excel)?
- [ ] ¿Periodicidad esperada de actualización de datos (diaria/semanal/manual)?

## 6) Entregables a pedirle a IT (salida de la reunión)

- [ ] Entorno objetivo definido: on-prem/cloud + responsable.
- [ ] Matriz de accesos y puertos aprobados.
- [ ] Instancia de PostgreSQL provisionada (o plan de provisión con fecha).
- [ ] URL interna objetivo y esquema de autenticación.
- [ ] Plan de backup/restore y monitoreo.
- [ ] Fecha estimada para piloto con usuarios.

## 7) Criterio de decisión (simple)

- **Go despliegue centralizado**: hay servidor + red + DB + seguridad mínima aprobada.
- **Plan B temporal**: operación local controlada por usuario clave, mientras IT habilita infraestructura.

---

## Mini resumen para dirección (1 minuto)

"Para usar ARS_MP en varias PCs necesitamos un despliegue centralizado con Python + PostgreSQL, acceso interno por red y criterios mínimos de seguridad/backup. Si IT confirma esos 4 puntos, el piloto multiusuario es viable sin depender de Docker en cada puesto."
