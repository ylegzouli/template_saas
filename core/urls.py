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
    path('start_task_gmap/', views.start_task_gmap, name='start_task_gmap'),
    # path('check_task_status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    path('check_task_status/<str:job_id>/', views.check_task_status, name='check_task_status'),
    path('check_task_status_gmap/<str:job_id>/', views.check_task_status_gmap, name='check_task_status_gmap '),
    
    path('end_task/<str:job_id>/', views.end_task, name='end_task'),
    path('load_score/<str:job_id>/', views.load_score, name='load_score'),
    path('app/settings', views.settings_view_ecom, name='settings'),
    path('app/settings_gmap', views.settings_view_gmap, name='settings_gmap'),

]
