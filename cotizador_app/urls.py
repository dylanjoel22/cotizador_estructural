from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cotizacion, name='cotizaciones'),
    path('crear/', views.crear_cotizacion, name='crear_cotizacion'),
    path('<int:cotizacion_id>/pdf/', views.generar_pdf, name='generar_pdf'),

    #CAMBIAR A PRIMARY KEY LUEGO/RECUERDA QUE ES SOLO MUESTRA
    path('detalle/', views.detalle_cotizacion, name='detalle_cotizacion'),
]
