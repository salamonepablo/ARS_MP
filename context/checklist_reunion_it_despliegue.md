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

## 8) Alternativa: cloud externo con URL pública (sin costo inicial)

- [ ] ¿IT permite consumo de una URL externa puntual vía proxy corporativo (allowlist por dominio)?
- [ ] ¿La política corporativa permite que datos operativos salgan a un proveedor externo?
- [ ] ¿Qué clasificación de datos aplica (interno/confidencial) y qué restricciones impone?
- [ ] ¿Se requiere contrato/DPA antes de subir datos a un tercero?

### Nota práctica (importante)

- Sí, es **posible** desplegar con costo cero inicial usando free tiers, pero no suele ser apto para producción estable.
- La mayoría de planes gratuitos tiene límites: suspensión por inactividad, cupos de CPU/RAM, almacenamiento acotado y sin SLA.
- Para piloto o demo interna puede servir; para operación diaria multiusuario conviene plan pago o infraestructura corporativa.
- Si se elige esta vía, pedir a IT al menos: allowlist de dominio, validación legal/compliance y criterio de continuidad.

## 9) Paso a paso sugerido para un despliegue Free Tier (piloto)

> Objetivo: tener una URL pública funcional para demo/piloto y validar acceso corporativo por proxy.

### 9.1 Preparación del repositorio (una sola vez)

- [ ] Confirmar que la app arranca localmente con variables de entorno (`DEBUG=False` en despliegue).
- [ ] Tener `requirements.txt` actualizado y comando de arranque definido.
- [ ] Definir lista mínima de variables de entorno: `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, zona horaria, etc.
- [ ] Verificar que no haya secretos en Git (`.env` fuera del repositorio).

### 9.2 Alta en proveedor PaaS con plan gratuito

- [ ] Elegir un proveedor con soporte Python web + PostgreSQL (o Postgres administrado aparte).
- [ ] Conectar el repositorio Git al proveedor.
- [ ] Crear servicio web y configurar:
  - Build command: instalación de dependencias + tareas de build necesarias.
  - Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
- [ ] Configurar variables de entorno desde panel seguro del proveedor.

### 9.3 Base de datos y migraciones

- [ ] Crear instancia PostgreSQL (free tier/trial o alternativa aprobada).
- [ ] Copiar cadena de conexión en `DATABASE_URL`.
- [ ] Ejecutar migraciones en el entorno (`python manage.py migrate`).
- [ ] Crear usuario administrador (`python manage.py createsuperuser`).

### 9.4 Publicación y prueba funcional

- [ ] Desplegar rama principal y obtener URL pública (ej: `https://ars-mp-demo.<proveedor>.com`).
- [ ] Probar login, vistas principales y flujo ETL mínimo con datos de prueba.
- [ ] Verificar logs de aplicación para errores de arranque/conexión DB.

### 9.5 Habilitación corporativa

- [ ] Pasar a IT: dominio exacto a permitir por proxy + puertos HTTPS requeridos.
- [ ] Solicitar confirmación de allowlist para usuarios de la red corporativa.
- [ ] Validar acceso desde al menos 2 PCs corporativas distintas.

### 9.6 Operación mínima durante piloto

- [ ] Definir responsable de reinicios/deploys y revisión de logs semanal.
- [ ] Acordar backup básico de DB (export diario/semanal según criticidad).
- [ ] Documentar límites esperables del free tier: cold start, suspensión por inactividad, cuota mensual.
- [ ] Definir criterio de salida a plan pago o migración a infraestructura corporativa.

---

## Mini resumen para dirección (1 minuto)

"Para usar ARS_MP en varias PCs necesitamos un despliegue centralizado con Python + PostgreSQL, acceso interno por red y criterios mínimos de seguridad/backup. Si IT confirma esos 4 puntos, el piloto multiusuario es viable sin depender de Docker en cada puesto."
