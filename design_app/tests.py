from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from .models import RoomPlan, Category, UserProfile
from .forms import CustomUserCreationForm, RoomPlanForm, RoomPlanStatusForm, CustomAuthenticationForm


# Проверка является ли пользователь администратором/менеджером/дизайнером
def is_staff_user(user):
    if not user.is_authenticated:
        return False
    try:
        profile = user.userprofile
        return profile.is_admin() or profile.is_manager()
    except UserProfile.DoesNotExist:
        return user.is_staff

# Проверка является ли пользователь администратором
def is_admin_user(user):
    if not user.is_authenticated:
        return False
    try:
        profile = user.userprofile
        return profile.is_admin()
    except UserProfile.DoesNotExist:
        return user.is_staff


# Проверка является ли пользователь дизайнером
def is_designer_user(user):
    if not user.is_authenticated:
        return False
    try:
        profile = user.userprofile
        return profile.is_designer()
    except UserProfile.DoesNotExist:
        return False


# Главная страница
def index(request):
    # Последние 4 выполненные заявки
    completed_applications = RoomPlan.objects.filter(
        status='COMPLETED'
    ).select_related('category', 'user').order_by('-upload_date')[:4]

    # Количество заявок в работе
    in_progress_count = RoomPlan.objects.filter(status='IN_PROGRESS').count()

    context = {
        'title': 'Design.pro — Студия Дизайна',
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    }
    return render(request, 'design_app/index.html', context)


# Регистрация - обновляем для создания профиля
def register_user(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Успешная регистрация! Добро пожаловать, {user.username}!")
            return redirect('index')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomUserCreationForm()

    context = {'form': form, 'title': 'Регистрация'}
    return render(request, 'design_app/register.html', context)


# Вход
def login_user(request):
    if request.user.is_authenticated:
        # Перенаправляем в зависимости от роли
        if is_staff_user(request.user):
            return redirect('admin_dashboard')
        else:
            return redirect('profile')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"С возвращением, {username}!")

                # Перенаправление в зависимости от роли
                if is_staff_user(user):
                    return redirect('admin_dashboard')
                else:
                    return redirect('profile')
        else:
            messages.error(request, "Неверный логин или пароль.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'design_app/login.html', {'form': form, 'title': 'Вход в систему'})


# Выход
def logout_user(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect('index')

# Личный кабинет пользователя - ТОЛЬКО для клиентов
@login_required
def user_profile(request):
    # Если пользователь staff - перенаправляем в админку
    if is_staff_user(request.user):
        return redirect('admin_dashboard')

    applications = RoomPlan.objects.filter(user=request.user).select_related('category')

    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'title': 'Личный кабинет',
        'room_plans': applications,
        'status_filter': status_filter,
    }
    return render(request, 'design_app/profile.html', context)


# Создание заявки - ТОЛЬКО для клиентов
@login_required
def create_room_plan(request):
    # Если пользователь staff - перенаправляем в админку
    if is_staff_user(request.user):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = RoomPlanForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RoomPlanForm()

    context = {'form': form, 'title': 'Создание заявки'}
    return render(request, 'design_app/create_room_plan.html', context)


# Удаление заявки - ТОЛЬКО для клиентов
@login_required
def delete_room_plan(request, plan_id):
    # Если пользователь staff - перенаправляем в админку
    if is_staff_user(request.user):
        return redirect('admin_dashboard')

    application = get_object_or_404(RoomPlan, id=plan_id, user=request.user)

    # Проверка можно ли удалить заявку
    if not application.can_be_deleted():
        messages.error(request, 'Нельзя удалить заявку, которая уже в работе или выполнена.')
        return redirect('profile')

    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Заявка успешно удалена!')
        return redirect('profile')

    context = {'room_plan': application, 'title': 'Удаление заявки'}
    return render(request, 'design_app/delete_room_plan.html', context)


# КАСТОМНАЯ АДМИН-ПАНЕЛЬ - для staff пользователей
@user_passes_test(is_staff_user, login_url='/login/')
def admin_dashboard(request):
    applications = RoomPlan.objects.all().select_related('user', 'category').order_by('-upload_date')

    # Фильтрация
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')

    if status_filter:
        applications = applications.filter(status=status_filter)
    if category_filter:
        applications = applications.filter(category_id=category_filter)

    categories = Category.objects.all()

    # Статистика
    stats = {
        'total': RoomPlan.objects.count(),
        'new': RoomPlan.objects.filter(status='NEW').count(),
        'in_progress': RoomPlan.objects.filter(status='IN_PROGRESS').count(),
        'completed': RoomPlan.objects.filter(status='COMPLETED').count(),
    }

    # Получаем профиль для отображения роли
    try:
        user_profile = request.user.userprofile
        user_role = user_profile.get_user_type_display()
    except UserProfile.DoesNotExist:
        user_role = "Администратор" if request.user.is_staff else "Пользователь"

    context = {
        'title': 'Панель управления',
        'applications': applications,
        'categories': categories,
        'stats': stats,
        'user_role': user_role,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'design_app/admin_dashboard.html', context)


# Редактирование заявки - для staff пользователей
@user_passes_test(is_staff_user, login_url='/login/')
def edit_application(request, plan_id):
    application = get_object_or_404(RoomPlan, id=plan_id)

    if request.method == 'POST':
        form = RoomPlanStatusForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус заявки успешно обновлен!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RoomPlanStatusForm(instance=application)

    context = {
        'form': form,
        'application': application,
        'title': 'Редактирование заявки'
    }
    return render(request, 'design_app/edit_application.html', context)


# Управление категориями - ТОЛЬКО для администраторов
@user_passes_test(is_admin_user, login_url='/login/')
def manage_categories(request):
    if request.method == 'POST':
        # Добавление категории
        if 'add_category' in request.POST:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            if name:
                Category.objects.create(name=name, description=description)
                messages.success(request, 'Категория успешно добавлена!')
            else:
                messages.error(request, 'Название категории не может быть пустым.')

        # Удаление категории
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category_name = category.name
            category.delete()
            messages.success(request, f'Категория "{category_name}" и все связанные заявки удалены!')

        return redirect('manage_categories')

    categories = Category.objects.annotate(
        applications_count=Count('roomplan')
    ).order_by('name')

    context = {
        'title': 'Управление категориями',
        'categories': categories
    }
    return render(request, 'design_app/manage_categories.html', context)