FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para la compilación
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar requerimientos
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel setuptools Cython && \
    pip install --no-cache-dir -r requirements.txt

# Segunda etapa: imagen final
FROM python:3.11-slim

WORKDIR /app

# Copiar los paquetes instalados de la etapa de construcción
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Crear usuario no root
RUN useradd -m -r appuser && \
    chown -R appuser:appuser /app

# Copiar el código de la aplicación
COPY backend/ .
RUN chown -R appuser:appuser /app

# Cambiar al usuario no root
USER appuser

# Variables de entorno
ENV PORT=8000
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
