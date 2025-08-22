import multiprocessing

# Configuración de servidor
bind = "0.0.0.0:$PORT"
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
