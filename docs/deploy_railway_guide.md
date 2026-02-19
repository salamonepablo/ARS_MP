# Guía de Despliegue en Railway - ARS_MP

> **Documento de referencia** para desplegar el MVP de ARS_MP en Railway.
> Seguir estos pasos cuando se decida hacer el deploy a producción.

## Resumen

| Item | Valor |
|------|-------|
| Plataforma | Railway (railway.app) |
| Costo | $5 USD crédito gratis/mes (suficiente para MVP) |
| Base de datos | PostgreSQL (incluido, 1-click) |
| URL pública | `https://ars-mp-production.up.railway.app` (o similar) |
| Tiempo estimado | 30-45 minutos |

---

## Prerequisitos

- [x] Cuenta GitHub con el repo `salamonepablo/ARS_MP`
- [ ] Cuenta en Railway (se crea con GitHub)
- [ ] Tailwind CSS compilado (`theme/static/css/dist/styles.css`)

---

## Paso 1: Crear cuenta en Railway

1. Ir a **https://railway.app**
2. Click en **"Login"** → **"Login with GitHub"**
3. Autorizar acceso a tu cuenta GitHub
4. Verificar email si te lo pide

---

## Paso 2: Agregar archivos de configuración al repo

### 2.1 Modificar `requirements.txt`

Agregar estas líneas al principio, después de Django:

```txt
# Production server
gunicorn>=22.0,<23.0
whitenoise>=6.7,<7.0
```

El archivo completo quedaría:

```txt
# Django core
Django>=5.0,<6.0

# Production server
gunicorn>=22.0,<23.0
whitenoise>=6.7,<7.0

# Database
psycopg[binary]>=3.2,<4.0

# ... resto igual ...
```

### 2.2 Crear archivo `Procfile` (en la raíz del proyecto)

```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
```

### 2.3 Crear archivo `railway.json` (en la raíz del proyecto)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/accounts/login/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### 2.4 Modificar `config/settings.py`

Agregar estas líneas:

**Después de la línea `ALLOWED_HOSTS = ...` (línea ~32):**

```python
# CSRF trusted origins for Railway
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "https://*.railway.app,https://*.up.railway.app"
).split(",")
```

**Después de `STATICFILES_DIRS = [...]` (línea ~181), agregar:**

```python
# Production static files
STATIC_ROOT = BASE_DIR / "staticfiles"
```

**En la lista `MIDDLEWARE`, agregar whitenoise después de SecurityMiddleware:**

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <-- AGREGAR ESTA LÍNEA
    "django.contrib.sessions.middleware.SessionMiddleware",
    # ... resto igual ...
]
```

### 2.5 Crear directorio `staticfiles` vacío

```bash
mkdir staticfiles
echo "" > staticfiles/.gitkeep
```

### 2.6 Commit y push de los cambios

```bash
git add .
git commit -m "feat: add Railway deployment configuration"
git push
```

---

## Paso 3: Crear proyecto en Railway

1. En Railway dashboard, click **"New Project"**
2. Seleccionar **"Deploy from GitHub repo"**
3. Buscar y seleccionar `salamonepablo/ARS_MP`
4. Railway detectará automáticamente que es un proyecto Python/Django

---

## Paso 4: Agregar PostgreSQL

1. En el proyecto Railway, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway crea la base de datos y conecta automáticamente las variables de entorno

---

## Paso 5: Configurar variables de entorno

En Railway, ir a **Settings** → **Variables** y agregar:

| Variable | Valor |
|----------|-------|
| `DJANGO_SECRET_KEY` | (generar uno nuevo, ver abajo) |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `.railway.app,.up.railway.app` |
| `DJANGO_DB_ENGINE` | `postgres` |

### Generar SECRET_KEY

Ejecutar en Python local:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

O usar: https://djecrety.ir/

**Nota:** Las variables de PostgreSQL (`POSTGRES_DB`, `POSTGRES_USER`, etc.) se configuran automáticamente cuando agregás la base de datos.

---

## Paso 6: Deploy

1. Railway hace deploy automático cuando detecta cambios en `main`
2. Ver logs en tiempo real en el dashboard
3. Esperar a que termine (2-5 minutos)

---

## Paso 7: Crear usuario administrador

Una vez desplegado, desde Railway:

1. Ir a la pestaña **"Settings"** del servicio web
2. Click en **"Open Shell"** (o usar Railway CLI)
3. Ejecutar:

```bash
python manage.py createsuperuser
```

**Alternativa con Railway CLI:**

```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Conectar al proyecto
railway link

# Ejecutar comando
railway run python manage.py createsuperuser
```

---

## Paso 8: Acceder a la aplicación

Railway proporciona una URL pública automática:

```
https://ars-mp-production.up.railway.app
```

(El nombre exacto depende de tu configuración)

---

## Verificación post-deploy

- [ ] La página de login carga correctamente
- [ ] Los estilos CSS se ven bien (Tailwind)
- [ ] Podés hacer login con el usuario creado
- [ ] La vista de flota muestra los 111 módulos (stub data)
- [ ] El Maintenance Planner funciona
- [ ] El export a Excel descarga correctamente

---

## Troubleshooting

### Error: "Static files not found"

```bash
# En Railway shell
python manage.py collectstatic --noinput
```

### Error: "CSRF verification failed"

Verificar que `CSRF_TRUSTED_ORIGINS` incluye el dominio de Railway.

### Error: "Database connection refused"

Verificar que PostgreSQL está corriendo y las variables de entorno están configuradas.

### Logs

Ver logs en Railway dashboard → pestaña **"Deployments"** → click en el deployment → **"View Logs"**

### Incident note: login fails with valid credentials

If login fails and logs show `USERS IN DB: []`, the web runtime database has no users yet.

Use Railway SSH and run Django with the container virtualenv:

```bash
railway ssh --service web
/opt/venv/bin/python manage.py shell -c "from django.contrib.auth.models import User; print('before=', list(User.objects.values_list('username', flat=True))); u, created = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True}); u.is_staff = True; u.is_superuser = True; u.set_password('CHANGE_ME'); u.save(); print('created=', created); print('after=', list(User.objects.values_list('username', flat=True)))"
```

Important: `python manage.py ...` in SSH may use system Python and fail with `No module named 'django'`. Always use `/opt/venv/bin/python`.

---

## Costos estimados

| Recurso | Consumo MVP | Costo |
|---------|-------------|-------|
| Web service | ~100 hrs/mes | $0 (dentro del free tier) |
| PostgreSQL | ~100 MB | $0 (dentro del free tier) |
| **Total** | | **$0/mes** |

El free tier de $5/mes es más que suficiente para un MVP con poco tráfico.

---

## Rollback

Si algo sale mal:

1. Railway guarda historial de deploys
2. Ir a **"Deployments"** → seleccionar deploy anterior → **"Redeploy"**

---

## Dominio personalizado (opcional)

Si querés usar un dominio propio:

1. En Railway → **Settings** → **Domains**
2. Click **"+ Custom Domain"**
3. Agregar tu dominio (ej: `ars-mp.tudominio.com`)
4. Configurar DNS en tu registrador (CNAME a Railway)

---

## Contacto Railway

- Documentación: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

---

*Documento generado el 18/02/2026 para ARS_MP - Argentinian Rolling Stock Maintenance Planner*
