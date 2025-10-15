from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/crear/', views.añadir_cliente, name='añadir_cliente'),
]
