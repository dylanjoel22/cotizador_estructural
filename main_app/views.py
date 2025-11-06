from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def inicio(request):
    return render(request, 'main_app/inicio.html')
@login_required
def perfiles_icha(request):
    return render(request, 'main_app/perfiles_icha.html')
