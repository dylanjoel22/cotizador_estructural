from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet

# Crea un router y registra nuestro ViewSet con él.
router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')

# Las URLs de la API son determinadas automáticamente por el router.
urlpatterns = [
    path('', include(router.urls)),
]
