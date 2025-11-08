import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DesignPro.settings')
django.setup()

from django.contrib.auth.models import User

# Создаем администратора
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@designpro.ru', 'admin')
    print("Администратор создан: логин - admin, пароль - admin")
else:
    print("Администратор уже существует")