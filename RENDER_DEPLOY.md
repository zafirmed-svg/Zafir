# Despliegue en Render (Guía rápida)

Este documento contiene los pasos y la checklist para redeplegar el backend Django en Render, junto con variables de entorno necesarias y comprobaciones habituales.

IMPORTANTE: estas instrucciones asumen que el repo contiene la configuración ya aplicada (archivo `render.yaml`, `backend/runtime.txt`, `Procfile` actualizado y `backend/requirements.txt`).

## Variables de entorno necesarias
Configura estas variables en la sección Environment / Environment Variables del servicio backend en Render:

- `POSTGRES_HOST` (host de la BBDD)
- `POSTGRES_PORT` (por defecto `5432`)
- `POSTGRES_DB` (nombre de la base de datos, e.g. `zafir_db`)
- `POSTGRES_USER` (usuario de la BD)
- `POSTGRES_PASSWORD` (contraseña)
- `DJANGO_SECRET_KEY` (valor secreto, en producción no uses `change-me`)
- `DEBUG` = `False` (en producción)
- `CORS_ALLOWED_ORIGINS` o `CORS_ALLOW_ALL_ORIGINS` según tu frontend
- Cualquier otra var que tu app necesite (SENTRY_DSN, ENVIRONMENT, etc.)

## Comportamiento del `render.yaml`
El `render.yaml` que generamos ejecuta:

1. `pip install -r backend/requirements.txt` (buildCommand)
2. startCommand:
   - `python manage.py migrate --noinput`
   - `python manage.py collectstatic --noinput`
   - `uvicorn backend.asgi:application --host 0.0.0.0 --port $PORT`

Esto garantiza que las migraciones se aplican en el arranque y que los ficheros estáticos se recogen.

Si prefieres ejecutar migraciones manualmente en deploy, edita `render.yaml` y elimina `migrate` del startCommand.

## Pasos para redeploy (manual)

1. Asegúrate de tener los cambios commiteados y pusheados a la rama que Render monitoriza (por ejemplo `main`):

```powershell
git add .
git commit -m "chore: actualizar config para deploy en Render"
git push origin main
```

2. En Render: ve al servicio backend → Deploys → Manual Deploy → Deploy latest commit. Alternativamente, si usas despliegue automático, push activará el build.

3. Revisa los logs del build y del runtime:
   - Build logs: pip install, instalación de dependencias.
   - Migrations: salida de `python manage.py migrate` (OK).
   - collectstatic: salida de `python manage.py collectstatic` (OK o advertencias si no está configurado storage).
   - Runtime: uvicorn arranca y enlaza al puerto. Revisa errores de import, errores de conexión a la DB o excepciones al iniciar.

## Comprobaciones post-deploy

- Abre la URL pública del servicio (Render muestra la `Service URL`). Prueba:
  - `/api/` → respuesta 200 con mensaje.
  - `/api/quotes/` → GET/POST según tu flujo.

- Si obtienes errores de autenticación con Postgres, revisa `POSTGRES_USER` y `POSTGRES_PASSWORD` en Environment variables.

- Si collectstatic falla y no usas almacenamiento remoto, asegúrate de tener `STATIC_ROOT` configurado en `backend/settings.py` y permisos adecuados.

## Comandos útiles (local) para probar antes de push

```powershell
cd backend
# crear entorno e instalar deps si no lo has hecho
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# ejecutar migraciones y levantar servidor local en el puerto 8000
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

# ejecutar tests
.\.venv\Scripts\python.exe manage.py test
```

## Errores comunes y soluciones rápidas

- `psycopg2 OperationalError: fe_sendauth: no password supplied` → falta `POSTGRES_PASSWORD` en env.
- `password authentication failed for user` → credenciales incorrectas.
- `No existe la relación "quotes_quote"` → migraciones no aplicadas; ejecutar `manage.py migrate`.
- Problemas con versiones de paquetes → ajustar `backend/requirements.txt` y volver a push.

## Opcional: ejecutar tests antes del deploy (recomendado)
- Puedes añadir un step en el pipeline (o en `render.yaml` en buildCommand) para ejecutar tests con `python manage.py test` y hacer que el build falle si los tests fallan.

## Nota sobre secretos y seguridad
- No subas `DJANGO_SECRET_KEY` al repo ni uses valores por defecto en producción. Usa Render Environment Secrets.

---
Si quieres, aplico automáticamente un job de CI (GitHub Actions) que ejecute tests y linters antes del push, o puedo añadir un pequeño script `deploy_render.sh` que hace `git push` y abre la URL. ¿Cuál prefieres? (A: action CI, B: script deploy)
