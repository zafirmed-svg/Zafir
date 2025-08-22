FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para la compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar requerimientos
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY backend/ .

# Variables de entorno
ENV PORT=8000
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
