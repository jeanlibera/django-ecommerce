from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register_page'),
    path('login/', views.login, name='login_page'),
    path('logout/', views.logout, name='logout_page'),
]