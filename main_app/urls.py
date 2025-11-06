from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('materiales_icha/', views.perfiles_icha, name='materiales_icha'),
]
