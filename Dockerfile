FROM python:3.11-slim

WORKDIR /app

# Configurar pip para usar mirrors alternativos y timeout más largo
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY backend/ .

# Crear y cambiar al usuario no root
RUN useradd -m -r appuser && \
    chown -R appuser:appuser /app
USER appuser

# Variables de entorno
ENV PORT=8000 \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
