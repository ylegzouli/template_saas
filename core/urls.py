# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    # path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    
    path('logout/', views.logout_view, name='logout'),
    
    
    path('app/e-commerce', views.app_view_ecommerce, name='app_ecommerce'),
    path('app/gmap', views.app_view_gmap, name='app_gmap'),

    
    path('start_task/', views.start_task_ecommerce, name='start_task'),
    path('check_task_status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    
    # path('app/settings', views.settings_view, name='settings'),

]
