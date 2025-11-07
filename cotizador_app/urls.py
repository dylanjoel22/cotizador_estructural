from django.urls import path
from . import views

app_name = 'cotizador_app'  # Agregando el app_name

urlpatterns = [
    path('', views.cotizacion, name='cotizaciones'),
    path('crear/', views.crear_cotizacion, name='crear_cotizacion'),
    path('<int:cotizacion_id>/pdf/', views.generar_pdf, name='generar_pdf'),
    path('detalle/', views.detalle_cotizacion, name='detalle_cotizacion'),
]