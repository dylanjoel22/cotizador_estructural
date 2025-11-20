from django.contrib import admin
from django.urls import path
from . import views



urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/crear/', views.añadir_cliente, name='añadir_cliente'),
    path('<int:pk>/detalle/', views.detalle_cliente, name='detalle_cliente'),
    path('<int:pk>/contactos/crear/', views.añadir_persona_contacto, name='añadir_persona_contacto'),
]
