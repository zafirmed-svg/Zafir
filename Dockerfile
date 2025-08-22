FROM python:3.11-slim

WORKDIR /app

# Copiar solo los archivos necesarios primero
COPY backend/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY backend/ .

# Exponer el puerto
EXPOSE 8000

# Copiar y dar permisos al script de inicio
COPY backend/start.sh /start.sh
RUN chmod +x /start.sh

# Comando para ejecutar la aplicación
CMD ["/start.sh"]
