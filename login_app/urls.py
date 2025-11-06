from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1. LOGIN: La raíz (/) usa la vista de Login de Django.
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'), 
    
    # 2. LOGOUT: Usa la vista de Logout de Django.
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    
    # 3. CAMBIO DE CONTRASEÑA, etc. (Todas vienen gratis)
    # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
]



