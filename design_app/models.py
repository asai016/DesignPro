from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from .models import RoomPlan, Category, UserProfile
import os
from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'example@mail.ru'
        })

# Кастомная форма регистрации с валидацией
class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=200,
        label='ФИО*',
        validators=[
            RegexValidator(
                regex='^[А-Яа-яёЁ\\s\\-]+$',
                message='ФИО должно содержать только кириллические буквы, пробелы и дефис'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Иванов Иван Иванович'
        })
    )

    username = forms.CharField(
        max_length=150,
        label='Логин*',
        validators=[
            RegexValidator(
                regex='^[a-zA-Z\\-]+$',
                message='Логин должен содержать только латинские буквы и дефис'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ivanov'
        })
    )

    # Email с валидацией
    email = forms.EmailField(
        label='Email*',
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru'
        })
    )
    agreement = forms.BooleanField(
        required=True,
        label='Я согласен на обработку персональных данных*',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2', 'agreement']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем Bootstrap классы ко всем полям
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'agreement':
                field.widget.attrs.update({'class': 'form-check-input'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                agreement=self.cleaned_data['agreement']
            )
        return user


# Форма создания заявки с валидацией файла
class RoomPlanForm(forms.ModelForm):
    def clean_plan_file(self):
        image = self.cleaned_data.get('plan_file')
        if image:
            # Проверка размера файла (2MB)
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 2MB')

            # Проверка формата
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Поддерживаются только форматы: JPG, JPEG, PNG, BMP')

        return image

    class Meta:
        model = RoomPlan
        fields = ['title', 'description', 'category', 'plan_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Дизайн гостиной в квартире'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите помещение, ваши пожелания по стилю, бюджету...',
                'rows': 4
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'plan_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название заявки*',
            'description': 'Описание*',
            'category': 'Категория*',
            'plan_file': 'Фото помещения или план*',
        }


# Форма для смены статуса администратором
class RoomPlanStatusForm(forms.ModelForm):
    class Meta:
        model = RoomPlan
        fields = ['status', 'design_image', 'admin_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'admin_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Комментарий для пользователя...',
                'rows': 3
            }),
            'design_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'Статус заявки',
            'design_image': 'Дизайн-проект',
            'admin_comment': 'Комментарий',
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        design_image = cleaned_data.get('design_image')
        admin_comment = cleaned_data.get('admin_comment')

        # Валидация согласно ТЗ
        if status == 'COMPLETED' and not design_image:
            raise forms.ValidationError({
                'design_image': 'Для статуса "Выполнено" необходимо прикрепить дизайн-проект'
            })

        if status == 'IN_PROGRESS' and not admin_comment:
            raise forms.ValidationError({
                'admin_comment': 'Для статуса "Принято в работу" необходимо добавить комментарий'
            })

        return cleaned_data


# Форма аутентификации
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ваш логин'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль'
        })