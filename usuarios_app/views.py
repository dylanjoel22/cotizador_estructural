"""
Vistas para la gestión de Clientes y Personas de Contacto.

Este módulo maneja las operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
para clientes y sus contactos asociados.
"""

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from .forms import ClienteForm, PersonaContactoForm
from .models import Cliente, PersonaContacto


def perfil(request):
    """Vista simple que renderiza el perfil del usuario actual."""
    return render(request, 'usuarios_app/perfil.html')


def añadir_cliente(request):
    """
    Crea un nuevo cliente en el sistema.
    
    Esta función implementa el patrón POST-redirect-GET:
    - GET: Muestra el formulario vacío
    - POST válido: Guarda y redirige (evita resubmit al refrescar)
    - POST inválido: Muestra errores en el mismo formulario
    """
    if request.method == 'POST':
        # Importante: request.FILES captura archivos subidos (como el logo)
        # Si no lo incluimos, el campo 'logo' siempre aparecerá vacío
        form = ClienteForm(request.POST, request.FILES)
        
        if form.is_valid():
            # save() crea el registro en BD y retorna la instancia guardada
            form.save()
            
            # Redirigimos después de guardar (patrón PRG: Post-Redirect-Get)
            # Esto evita que el usuario pueda re-guardar el mismo cliente al refrescar la página
            return redirect(reverse('clientes'))
    else:
        # Request GET: mostramos un formulario vacío
        form = ClienteForm()
    
    # Este contexto se usa tanto para GET como para POST con errores
    context = {
        'form': form,
        'page_title': 'Crear Nuevo Cliente'
    }
    return render(request, 'usuarios_app/añadir_cliente.html', context)


def clientes(request):
    """
    Lista todos los clientes registrados.
    
    Esta es una vista simple de listado. Más adelante podríamos añadir:
    - Paginación (usando Django Paginator)
    - Filtros (por ciudad, activo/inactivo, etc.)
    - Búsqueda (usando Q objects)
    """
    clientes = Cliente.objects.all()
    
    context = {
        'clientes': clientes
    }
    return render(request, 'usuarios_app/clientes.html', context)


def detalle_cliente(request, pk):
    """
    Muestra la información detallada de un cliente y sus contactos asociados.
    
    Args:
        pk (int): Primary Key del cliente a mostrar
        
    Returns:
        HttpResponse: Renderiza el template con el cliente y sus contactos
    """
    # get_object_or_404 es más seguro que .get() porque retorna 404 si no existe
    # en vez de lanzar una excepción DoesNotExist
    cliente = get_object_or_404(Cliente, pk=pk)
    
    # Filtramos contactos por la relación ForeignKey
    # Alternativa equivalente: cliente.contactos.all() (usando related_name)
    contactos = PersonaContacto.objects.filter(cliente=cliente)
    
    context = {
        'cliente': cliente,
        'contactos': contactos,
        'page_title': f'Detalle del Cliente: {cliente.nombre}'
    }
    return render(request, 'usuarios_app/clientes_contactos.html', context)


def añadir_persona_contacto(request, pk):
    """
    Crea una nueva persona de contacto para un cliente específico.
    
    Esta función usa una técnica avanzada: pre-asignar la ForeignKey
    antes de mostrar el formulario. Esto evita tener que ocultar el campo
    'cliente' en el template o manejarlo manualmente.
    
    Args:
        pk (int): Primary Key del cliente al que pertenece este contacto
    """
    # Obtenemos el cliente al que vamos a asociar el contacto
    cliente = get_object_or_404(Cliente, pk=pk)

    # Creamos una instancia nueva CON la FK ya asignada
    # Esto es como hacer: contacto = PersonaContacto(); contacto.cliente = cliente
    new_contact = PersonaContacto(cliente=cliente)

    if request.method == 'POST':
        # Pasamos request.POST Y la instancia pre-asignada al formulario
        # Cuando hagamos save(), Django guardará esta instancia con los datos del POST
        form = PersonaContactoForm(request.POST, instance=new_contact)
        
        if form.is_valid():
            form.save()
            
            # Redirigimos de vuelta al detalle del cliente
            # Esto permite al usuario ver inmediatamente el contacto que acaba de crear
            return redirect('detalle_cliente', pk=cliente.pk)
    else:
        # GET: Mostramos el formulario con la instancia pre-asignada
        form = PersonaContactoForm(instance=new_contact)
    
    context = {
        'form': form,
        'cliente': cliente,
        'page_title': 'Añadir Persona de Contacto'
    }
    return render(request, 'usuarios_app/contactos_crear.html', context)


def get_contactos_por_empresa(request):
    """
    Endpoint AJAX que retorna los contactos de un cliente en formato JSON.
    
    Este endpoint se usa típicamente en formularios dinámicos donde el usuario
    selecciona una empresa y queremos poblar un dropdown de contactos automáticamente.
    
    Returns:
        JsonResponse: Lista de contactos con formato [{"id": 1, "nombre": "Juan"}, ...]
    """
    empresa_id = request.GET.get('empresa_id')
    
    if not empresa_id:
        # Si no nos dan ID, retornamos lista vacía
        return JsonResponse([], safe=False)
    
    # OPTIMIZACIÓN: Usamos .values() en vez de serializar objetos completos
    # Esto genera un query mucho más eficiente que solo selecciona las columnas que necesitamos:
    # SELECT id, nombre FROM personacontacto WHERE cliente_id = X
    # en vez de: SELECT * FROM personacontacto WHERE cliente_id = X
    contactos = PersonaContacto.objects.filter(
        cliente_id=empresa_id
    ).values('id', 'nombre').order_by('nombre')
    
    # safe=False es necesario porque estamos retornando una lista, no un dict
    # Por defecto, Django solo permite serializar diccionarios por seguridad
    return JsonResponse(list(contactos), safe=False)


def get_clientes_json(request):
    """
    Endpoint AJAX que retorna todos los clientes activos en formato JSON.
    
    Útil para refrescar selectores dinámicos después de crear un nuevo cliente
    sin tener que recargar toda la página.
    
    Returns:
        JsonResponse: Lista de clientes con formato [{"id": 1, "nombre": "Empresa ABC"}, ...]
    """
    # Misma optimización que en get_contactos_por_empresa
    # Solo seleccionamos las columnas que necesitamos para reducir el tráfico de red
    clientes = Cliente.objects.all().values('id', 'nombre').order_by('nombre')
    
    return JsonResponse(list(clientes), safe=False)