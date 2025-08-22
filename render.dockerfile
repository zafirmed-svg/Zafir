# Use Python 3.11.4 slim image
FROM python:3.11.4-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create a non-root user
RUN useradd -m -r appuser && \
    chown -R appuser:appuser /app
USER appuser

# Start command using gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "main:app"]
