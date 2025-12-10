
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [

    #Ruta del administrador
    path('admin/', admin.site.urls),

    #Ruta de la aplicacion de login
    path('', include('login_app.urls')),

    #Ruta de la aplicacion principal
    path('home/', include('main_app.urls')),

    #Ruta de la aplicacion de usuarios y login
    path('usuarios/', include('usuarios_app.urls')),

    #Ruta de la aplicacion de cotizaciones
    path('cotizaciones/', include('cotizador_app.urls')),

    #Ruta de la API de perfiles
    path('api/', include('profiles_api.urls')),
]

# ✅ Django Debug Toolbar - Solo en modo DEBUG
# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
