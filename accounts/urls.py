from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register_page'),
    path('login/', views.login, name='login_page'),
    path('logout/', views.logout, name='logout_action'),
    path('dashboard/', views.dashboard, name='dashboard_page'),
    path('', views.dashboard),

    path('activate/<uidb64>/<token>/', views.activate, name='activate_action'),
    path('forgot-password/', views.forgot_password, name='forgot_password_page'),
    path('reset-password-validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate_action'),
    path('reset-password/', views.reset_password, name='reset_password_page'),
]