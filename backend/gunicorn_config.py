import multiprocessing

# Configuración de servidor
import os
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120

# Configuración de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configuración de aplicación
wsgi_app = "main:app"
pythonpath = "."
