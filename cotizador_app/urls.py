from django.urls import path
from . import views

app_name = 'cotizador_app'  # Agregando el app_name

urlpatterns = [
    path('', views.cotizacion, name='cotizaciones'),
    path('crear/', views.crear_cotizacion, name='crear_cotizacion'),
    path('<int:cotizacion_id>/pdf/', views.generar_pdf, name='generar_pdf'),
    path('detalle/', views.detalle_cotizacion, name='detalle_cotizacion'),
    path('<int:cotizacion_id>/eliminar/', views.eliminar_cotizacion, name='eliminar_cotizacion'),
    # API endpoints for AJAX calls
    path('api/search/', views.cotizacion_search_api, name='cotizacion_search_api'),
]