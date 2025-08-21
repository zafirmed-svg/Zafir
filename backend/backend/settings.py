# ... (importaciones existentes) ...
import os
from dotenv import load_dotenv
import dj_database_url # Importar dj_database_url

# ... (BASE_DIR y load_dotenv existentes) ...

# Render detecta esta variable de entorno. Si existe, estamos en producción.
IS_RENDER = 'RENDER' in os.environ

# SECURITY WARNING: keep the secret key used in production secret!
# Leer la SECRET_KEY desde las variables de entorno en producción
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-se^uk7uys)0#()!&((_8l7!otjo524^cchurh3a_qezl_7vxu$')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG será False en Render, y True localmente
DEBUG = not IS_RENDER

# Configurar los hosts permitidos
ALLOWED_HOSTS = []

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition
# ... (INSTALLED_APPS existente) ...

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Añadir WhiteNoise aquí
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... (resto del middleware) ...
]

# ... (ROOT_URLCONF, TEMPLATES, WSGI_APPLICATION existentes) ...

# Database configuration
if IS_RENDER:
    # Usar la base de datos PostgreSQL de Render
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Usar la base de datos MySQL local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }

# ... (resto de settings) ...

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Esta configuración es para WhiteNoise
if IS_RENDER:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'