from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),

    # Восстановление пароля
    re_path(r'^password-reset/$',
         auth_views.PasswordResetView.as_view(
             template_name='design_app/registration/password_reset_form.html',
             email_template_name='design_app/registration/password_reset_email.html'
         ),
         name='password_reset'),
    re_path(r'^password-reset/done/$',
         auth_views.PasswordResetDoneView.as_view(
             template_name='design_app/registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    re_path(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='design_app/registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    re_path(r'^password-reset-complete/$',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='design_app/registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Личный кабинет и заявки
    path('profile/', views.user_profile, name='profile'),
    path('room-plan/create/', views.create_room_plan, name='create_room_plan'),
    re_path(r'^room-plan/delete/(?P<plan_id>\d+)/$', views.delete_room_plan, name='delete_room_plan'),

    # Админ-панель
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    re_path(r'^admin-dashboard/application/(?P<plan_id>\d+)/$', views.edit_application, name='edit_application'),
    path('admin-dashboard/categories/', views.manage_categories, name='manage_categories'),
]