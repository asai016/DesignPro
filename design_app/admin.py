from django.contrib import admin
from django.utils.html import format_html
from .models import Category, UserProfile, RoomPlan


# Настройка для категорий
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'applications_count']
    search_fields = ['name', 'description']
    list_filter = ['name']

    def applications_count(self, obj):
        return obj.roomplan_set.count()

    applications_count.short_description = 'Кол-во заявок'


# Настройка для профилей пользователей
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'user_type', 'agreement']
    search_fields = ['full_name', 'user__username']
    list_filter = ['user_type', 'agreement']
    raw_id_fields = ['user']


# Настройка для заявок
@admin.register(RoomPlan)
class RoomPlanAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'user',
        'category',
        'status_badge',
        'upload_date',
        'plan_file_preview'
    ]
    list_filter = ['status', 'category', 'upload_date']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['upload_date', 'plan_file_preview', 'design_image_preview']
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'description', 'category')
        }),
        ('Файлы', {
            'fields': ('plan_file', 'plan_file_preview', 'design_image', 'design_image_preview')
        }),
        ('Статус и комментарии', {
            'fields': ('status', 'admin_comment', 'assigned_to')
        }),
        ('Даты', {
            'fields': ('upload_date',),
            'classes': ('collapse',)
        })
    )

    def status_badge(self, obj):
        colors = {
            'NEW': 'blue',
            'IN_PROGRESS': 'orange',
            'COMPLETED': 'green'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Статус'

    def plan_file_preview(self, obj):
        if obj.plan_file:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 100px; max-width: 100px;" /></a>',
                obj.plan_file.url,
                obj.plan_file.url
            )
        return "—"

    plan_file_preview.short_description = 'Предпросмотр плана'

    def design_image_preview(self, obj):
        if obj.design_image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 100px; max-width: 100px;" /></a>',
                obj.design_image.url,
                obj.design_image.url
            )
        return "—"

    design_image_preview.short_description = 'Предпросмотр дизайна'

    # Действия для массового изменения статуса
    actions = ['mark_as_new', 'mark_as_in_progress', 'mark_as_completed']

    def mark_as_new(self, request, queryset):
        updated = queryset.update(status='NEW')
        self.message_user(request, f'{updated} заявок помечено как "Новые"')

    mark_as_new.short_description = 'Пометить как "Новые"'

    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='IN_PROGRESS')
        self.message_user(request, f'{updated} заявок помечено как "В работе"')

    mark_as_in_progress.short_description = 'Пометить как "В работе"'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} заявок помечено как "Выполнено"')

    mark_as_completed.short_description = 'Пометить как "Выполнено"'

admin.site.site_header = 'Design.pro - Административная панель'
admin.site.site_title = 'Design.pro Admin'
admin.site.index_title = 'Управление порталом Design.pro'