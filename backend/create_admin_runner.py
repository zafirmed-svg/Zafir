import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email='admin@example.com', password='zafir2025')
    print('created admin user')
else:
    print('admin exists')
