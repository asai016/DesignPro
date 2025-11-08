import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DesignPro.settings')
django.setup()

from django.contrib.auth.models import User
from design_app.models import UserProfile

# Назначаем роли пользователям
users_roles = {
    'admin': 'ADMIN',           # Администратор - полный доступ
    'designer1': 'DESIGNER',    # Дизайнер - может менять статусы
    'manager1': 'MANAGER',      # Менеджер - может просматривать заявки
}

for username, role in users_roles.items():
    try:
        user = User.objects.get(username=username)
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.user_type = role
        profile.full_name = f"Тестовый {role}"
        profile.agreement = True
        profile.save()
        print(f"✅ Назначена роль {role} пользователю {username}")
    except User.DoesNotExist:
        print(f"⚠️ Пользователь {username} не найден")

print("🎉 Роли назначены!")