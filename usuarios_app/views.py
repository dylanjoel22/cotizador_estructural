from django.shortcuts import render,redirect,reverse
from .forms import ClienteForm, PersonaContactoForm
from .models import Cliente, PersonaContacto
from django.shortcuts import get_object_or_404

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


def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    contactos = PersonaContacto.objects.filter(cliente=cliente)
    context = {
        'cliente': cliente,
        'contactos': contactos,
        'page_title': f'Detalle del Cliente: {cliente.nombre}'
    }
    return render(request, 'usuarios_app/clientes_contactos.html', context)
    

def añadir_persona_contacto(request, pk):
    # 1. Obtener el Cliente.
    cliente = get_object_or_404(Cliente, pk=pk)

    # 2. Creamos una instancia del modelo con la FK YA ASIGNADA
    contacto_con_cliente_asignado = PersonaContacto(cliente=cliente)

    if request.method == 'POST':
        # 3. Pasar el POST data Y la instancia pre-asignada al formulario
        form = PersonaContactoForm(
            request.POST, 
            instance=contacto_con_cliente_asignado
        ) 
        
        if form.is_valid():
            # 💥 4. ¡AQUÍ ESTABA EL CÓDIGO FALTANTE! 💥
            # El objeto se guarda
            form.save()
            
            # AÑADIMOS LA REDIRECCIÓN DE ÉXITO:
            # Usamos el nombre de URL globalmente único según tu petición.
            return redirect('detalle_cliente', pk=cliente.pk) # ⬅️ FIX AÑADIDO
        
    else:
        # Petición GET: Pasamos la instancia al formulario
        form = PersonaContactoForm(instance=contacto_con_cliente_asignado)
    
    context = {
        'form': form,
        'cliente': cliente,
        'page_title': 'Añadir Persona de Contacto'
    }
    
    # Si form.is_valid() falla, el código llega aquí y renderiza el formulario con errores.
    return render(request, 'usuarios_app/contactos_crear.html', context)