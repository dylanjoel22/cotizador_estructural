from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('inicio/', views.inicio, name='inicio'),
    path('clientes/', views.clientes, name='clientes'),
    path('materiales_icha/', views.perfiles_icha, name='materiales_icha'),

    
]
