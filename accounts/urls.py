from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register_page'),
    path('login/', views.login, name='login_page'),
    path('logout/', views.logout, name='logout_action'),
    path('dashboard/', views.dashboard, name='dashboard_page'),
    path('', views.dashboard),

    path('activate/<uidb64>/<token>/', views.activate, name='activate_action')
]