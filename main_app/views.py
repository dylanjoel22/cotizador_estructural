from django.shortcuts import render

# Create your views here.
def inicio(request):
    return render(request, 'main_app/inicio.html')

def clientes(request):
    return render(request, 'main_app/clientes.html')

def perfiles_icha(request):
    return render(request, 'main_app/perfiles_icha.html')