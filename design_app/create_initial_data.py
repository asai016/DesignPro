import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DesignPro.settings')
django.setup()

from design_app.models import Category

# Создаем начальные категории согласно ТЗ
initial_categories = [
    {'name': '3D-дизайн', 'description': 'Трехмерное проектирование интерьера'},
    {'name': '2D-дизайн', 'description': 'Двухмерные чертежи и планы'},
    {'name': 'Эскиз', 'description': 'Предварительные наброски и концепции'},
    {'name': 'Полный дизайн-проект', 'description': 'Комплексное проектирование интерьера'},
]

for category_data in initial_categories:
    category, created = Category.objects.get_or_create(
        name=category_data['name'],
        defaults={'description': category_data['description']}
    )
    if created:
        print(f' Создана категория: {category.name}')
    else:
        print(f' Категория уже существует: {category.name}')

print("🎉 Начальные данные созданы!")