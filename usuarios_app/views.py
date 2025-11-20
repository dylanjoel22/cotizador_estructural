from django.shortcuts import render,redirect,reverse
from .forms import ClienteForm
from .models import Cliente

# Create your views here.

def perfil(request):
    return render(request, 'usuarios_app/perfil.html')


def añadir_cliente(request):
    """
    Maneja la lógica para crear un nuevo cliente, incluyendo la subida de archivos (logo).
    """
    
    if request.method == 'POST':
        # Inicializa el formulario con datos POST y FILES (archivos subidos)
        form = ClienteForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Guarda la instancia del cliente y el archivo del logo
            cliente = form.save()
            
    else: 
        # Para solicitudes GET, inicializa un formulario vacío
        form = ClienteForm()
    
    # Renderizado final: se ejecuta para GET o POST inválido.
    context = {
        'form': form, # Garantizado que el objeto 'form' existe aquí
        'page_title': 'Crear Nuevo Cliente'
    }
    return render(request, 'usuarios_app/añadir_cliente.html', context)

   

def clientes(request):
    clientes = Cliente.objects.all()
    context = {
        'clientes': clientes
    }
    return render(request, 'usuarios_app/clientes.html', context)

