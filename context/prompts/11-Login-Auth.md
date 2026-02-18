## 🚀 11 - Login y Autenticación (prompt para IA)

### Objetivo

Agregar una instancia de **login** al ingresar al sistema, permitiendo autenticación de usuarios de manera segura y alineada a buenas prácticas (OWASP, encriptación moderna, sin exponer secretos en el repo).

### Alcance funcional

- Al acceder al sistema, se debe requerir login.
- El usuario podrá autenticarse usando:
	- Usuario de Windows (si es posible obtenerlo del entorno, ej. `os.getlogin()` o similar).
	- O bien, email corporativo de Trenes Argentinos.
- No hay perfiles ni permisos diferenciados por ahora (solo acceso/no acceso).
- No se permite modificar datos desde la UI, solo visualizar.

### Contexto

- Proyecto: `ARS_MP`
- Backend: Django + PostgreSQL
- SO/Shell: Windows + PowerShell 7 (`pwsh`)
- Despliegue futuro: server o cloud corporativo (ajustar integración según requerimientos de IT)

Convenciones del proyecto (según `AGENTS.md`):

- Responder en español.
- Código en inglés (nombres de funciones/variables).
- Documentación técnica en inglés en `docs/`.
- Reglas/criterios de negocio en español en `context/`.
- `core/` no depende de Django.

### Instrucciones para la IA

Actuá como developer senior. Implementá la autenticación siguiendo buenas prácticas de seguridad:

- Cumplir con los principios y normas **OWASP** para autenticación y gestión de contraseñas.
- - Cumplir OWASP y buenas prácticas de seguridad.
  - No se si OWASP será posible en todos caso porque por ejemplo la pwd mía de ingreso a la pc es muy débil, tipo xxxx-nnn, pero al menos hay que usar un algoritmo de hashing robusto para almacenar las contraseñas.
- Utilizar encriptación de contraseñas con algoritmo robusto y actualizado (ej. Argon2, bcrypt, PBKDF2).
- No subir secretos, claves ni archivos sensibles al repo (usar `.env` y variables de entorno para credenciales/configuración).
- Crear las tablas necesarias en PostgreSQL para usuarios (mínimo: id, username/email, password_hash, is_active, created_at, updated_at).
- Si es posible, permitir login automático usando el usuario de Windows (Single Sign-On) o, si no, login clásico con email corporativo y contraseña.
- Dejar preparado el sistema para poder adaptar la autenticación a SSO corporativo o integración con Active Directory en el futuro.

### Entregables esperados

- Formulario de login accesible al ingresar al sistema.
- Modelo/tablas de usuario en PostgreSQL, migraciones incluidas.
- Contraseñas almacenadas encriptadas (nunca en texto plano).
- No subir archivos `.env`, credenciales ni secretos al repo.
- Documentar en `docs/` cómo configurar credenciales y variables de entorno para desarrollo.

### Restricciones

- Cumplir OWASP y buenas prácticas de seguridad.
  - No se si OWASP será posible en todos caso porque por ejemplo la pwd mía de ingreso a la pc es muy débil, tipo xxxx-nnn, pero al menos hay que usar un algoritmo de hashing robusto para almacenar las contraseñas.
- No subir secretos ni archivos sensibles al repo.
- No almacenar contraseñas en texto plano.
- No modificar datos de la base legacy.