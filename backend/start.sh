#!/bin/sh

# Esperar a que la base de datos esté lista (si es necesario)
# sleep 5

# Configurar las variables de entorno
export PYTHONPATH=/app
export PORT="${PORT:-8000}"

# Iniciar la aplicación
exec uvicorn backend.asgi:application --host 0.0.0.0 --port $PORT
