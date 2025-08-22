"""
ASGI application entrypoint
"""
from main import app

# This is the ASGI application to be used by Gunicorn
application = app
