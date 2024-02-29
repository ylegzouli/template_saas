# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    
    path('logout/', views.logout_view, name='logout'),
    
    
    path('app/ecommerce', views.app_view_ecommerce, name='app'),
    path('app/gmap', views.app_view_gmap, name='app_gmap'),

    # path('export/', views.export_to_excel, name='export_to_excel'),
    # path('app/main/2', views.app_view_2, name='app_2'),
    # path('app/settings', views.settings_view, name='settings'),

]
