"""
Vistas para el sistema de Cotizaciones.

Maneja la creación, visualización y generación de PDFs de cotizaciones.
"""

from json import JSONDecodeError  # ✅ FIX BAJO-001: Import específico
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from .forms import CotizacionForm
from .models import Cotizacion, MaterialEstructural, CostoAdicional
from usuarios_app.models import Cliente

# Configurar logger para este módulo
logger = logging.getLogger(__name__)



@login_required
def cotizacion(request):
    """
    Lista todas las cotizaciones ordenadas por fecha de creación.
    
    Las mostramos de más reciente a más antigua para que el usuario
    vea primero lo que acaba de crear.
    
    Optimización: Usamos select_related('cliente') para evitar N+1 queries
    cuando el template acceda a cotizacion.cliente.nombre
    
    Optimización CRÍTICO-003: prefetch_related para materiales y costos
    evita N+1 queries al acceder a calculated_total en el template
    """
    cotizaciones = Cotizacion.objects.select_related('cliente')\
        .prefetch_related('materiales_estructurales', 'costos_adicionales')\
        .order_by('-fecha_creacion')
    
    return render(request, 'coti_app/cotizacion.html', {
        'cotizaciones': cotizaciones,
    })






@login_required
def detalle_cotizacion(request):
    """Vista de detalle de una cotización específica."""
    return render(request, 'coti_app/detalle_cotizacion.html')





@login_required
def crear_cotizacion(request):
    """
    Crea una nueva cotización con sus materiales y costos asociados.
    
    Esta vista usa transaction.atomic() para garantizar que todo se guarde
    correctamente o nada se guarde en caso de error (integridad de datos).
    """
    error_message = None


    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        
        if form.is_valid():
            try:
                # transaction.atomic() crea un bloque transaccional
                # Si algo falla dentro del bloque, TODA la transacción se revierte
                # Esto evita que tengamos una cotización guardada sin sus materiales
                with transaction.atomic():
                    # Guardamos primero la cotización principal
                    cotizacion = form.save()

                    # Creamos los materiales estructurales desde el JSON
                    structural_data = form.cleaned_data.get('structural_items_json')
                    if structural_data:
                        _create_structural_materials(cotizacion, structural_data)

                    # Creamos los costos adicionales desde el JSON
                    overhead_data = form.cleaned_data.get('overhead_items_json')
                    if overhead_data:
                        _create_additional_costs(cotizacion, overhead_data)
                    
                    # Si llegamos aquí, todo salió bien. Redirigimos al listado
                    return redirect(reverse('cotizador_app:cotizaciones'))

            except JSONDecodeError as e:
                logger.error(f"JSON inválido en cotización: {e}", exc_info=True)
                error_message = "Error: La estructura de datos del formulario es inválida."
            except IntegrityError as e:
                logger.error(f"Error de integridad en BD al crear cotización: {e}", exc_info=True)
                error_message = "No se pudo guardar la cotización. Verifique que los datos no estén duplicados."
            except ValueError as e:
                logger.error(f"Error de validación en cotización: {e}", exc_info=True)
                error_message = "Datos inválidos en el formulario. Verifique los valores numéricos."
            except Exception as e:
                logger.critical(f"Error inesperado al crear cotización: {e}", exc_info=True)
                error_message = "Ocurrió un error inesperado. Por favor, contacte al administrador."
        else:
            error_message = "Por favor, corrija los errores del formulario."
    else:
        # GET: mostramos un formulario vacío
        form = CotizacionForm()

    # Cargamos todos los clientes para el dropdown
    # TODO: Si hay muchos clientes, considerar usar select2 con paginación
    clientes_disponibles = Cliente.objects.all()
    
    context = {
        'form': form,
        'error_message': error_message,
        'clientes_disponibles': clientes_disponibles,
    }
    
    return render(request, 'coti_app/crear_cotizacion.html', context)


def _create_structural_materials(cotizacion, items_data):
    """
    Función helper que crea múltiples registros de MaterialEstructural.
    
    Separamos esta lógica en una función para:
    1. Mantener crear_cotizacion más legible
    2. Facilitar testing aislado
    3. Permitir reutilización si es necesario
    
    Args:
        cotizacion: Instancia de Cotizacion padre
        items_data: Lista de diccionarios con datos de materiales
    """
    # Usamos bulk_create en vez de create() dentro de un loop
    # Esto reduce las queries a la BD de N a 1 (mucho más rápido)
    materials_to_create = [
        MaterialEstructural(
            cotizacion=cotizacion,
            material_nombre=item.get('material_nombre', ''),
            largo_m=item.get('largo_m', 0.0),
            unidad_comercial=item.get('unidad_comercial', 0.0),
            cant_necesaria=item.get('cant_necesaria', 1),
            cant_a_comprar=item.get('cant_a_comprar', 1),
            valor_unitario_m=item.get('valor_unitario_m', 0.0),
            peso_kg_m=item.get('peso_kg_m', 0.0),
        )
        for item in items_data
    ]
    
    MaterialEstructural.objects.bulk_create(materials_to_create)


def _create_additional_costs(cotizacion, items_data):
    """
    Función helper que crea múltiples registros de CostoAdicional.
    
    Similar a _create_structural_materials, usa bulk_create para optimización.
    
    Args:
        cotizacion: Instancia de Cotizacion padre
        items_data: Lista de diccionarios con datos de costos
    """
    costs_to_create = [
        CostoAdicional(
            cotizacion=cotizacion,
            descripcion=item.get('descripcion', ''),
            unidad=item.get('unidad', 'Unidad'),
            cantidad=item.get('cantidad', 1.0),
            valor_unitario=item.get('valor_unitario', 0.0),
        )
        for item in items_data
    ]
    
    CostoAdicional.objects.bulk_create(costs_to_create)


# ========================================================================
# GENERACIÓN DE PDF - Dividido en funciones pequeñas y reutilizables
# ========================================================================


@login_required
def generar_pdf(request, cotizacion_id):
    """
    Genera un PDF profesional con los detalles de la cotización.
    
    Esta función coordina la generación del PDF pero delega el trabajo
    específico a funciones helper. Esto nos da:
    - Código más legible y mantenible
    - Facilidad para testear cada sección por separado
    - Posibilidad de reutilizar secciones en otros reportes
    """
    # Obtenemos la cotización con sus relaciones
    # select_related optimiza el query para evitar N+1
    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related('cliente'),
        id=cotizacion_id
    )
    
    # Configuramos la respuesta HTTP como PDF
    response = HttpResponse(content_type='application/pdf')
    filename = _generate_pdf_filename(cotizacion)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Creamos el documento con márgenes personalizados
    doc = SimpleDocTemplate(
        response, 
        pagesize=letter,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Story es una lista de elementos que ReportLab renderizará en orden
    story = []
    styles = getSampleStyleSheet()
    
    # Construimos cada sección del PDF
    _build_header_section(story, cotizacion, styles)
    _build_materials_section(story, cotizacion, styles)
    _build_costs_section(story, cotizacion, styles)
    _build_total_section(story, cotizacion, styles)
    _build_notes_section(story, cotizacion, styles)
    
    # Renderizamos el PDF completo
    doc.build(story)
    return response



def _generate_pdf_filename(cotizacion):
    """
    Genera un nombre de archivo descriptivo y seguro para el PDF.
    
    Sanitiza el nombre del proyecto para prevenir path traversal y
    caracteres problemáticos en sistemas de archivos.
    
    Ejemplo: "cotizacion_Proyecto_Edificio_ABC_123.pdf"
    """
    import re
    
    # Eliminar caracteres peligrosos, permitir solo alfanuméricos, espacios, guiones y guiones bajos
    safe_project_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', cotizacion.proyecto_nombre)
    
    # Limitar largo para evitar nombres de archivo excesivamente largos
    safe_project_name = safe_project_name[:50].strip()
    
    # Reemplazar espacios por guiones bajos
    safe_project_name = safe_project_name.replace(' ', '_')
    
    # Si después de sanitizar quedó vacío, usar un nombre por defecto
    if not safe_project_name:
        safe_project_name = "sin_nombre"
    
    return f"cotizacion_{safe_project_name}_{cotizacion.id}.pdf"



def _build_header_section(story, cotizacion, styles):
    """
    Construye la sección de encabezado del PDF con información general.
    
    Incluye: Título, ID, fecha, cliente
    """
    # Título principal
    story.append(Paragraph(
        f"<b>REGISTRO DE COSTOS INTERNOS - PROYECTO: {cotizacion.proyecto_nombre.upper()}</b>", 
        styles['Heading1']
    ))
    story.append(Spacer(1, 0.2 * inch))

    # Información básica
    cliente_nombre = cotizacion.cliente.nombre if cotizacion.cliente else "N/A (Sin Cliente Asociado)"
    
    story.append(Paragraph(f"<b>ID Cotización:</b> {cotizacion.id}", styles['Normal']))
    story.append(Paragraph(
        f"<b>Fecha de Registro:</b> {cotizacion.fecha_creacion.strftime('%d-%m-%Y %H:%M')}", 
        styles['Normal']
    ))
    story.append(Paragraph(f"<b>Cliente:</b> {cliente_nombre}", styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))


def _build_materials_section(story, cotizacion, styles):
    """
    Construye la tabla de materiales estructurales con totales.
    
    Esta tabla incluye: material, largo, unidad comercial, cantidad,
    valores unitarios y totales, pesos.
    """
    story.append(Paragraph("<b>1. Material Estructural (Metales, Planchas, etc.)</b>", styles['h2']))
    story.append(Spacer(1, 0.1 * inch))

    # Encabezados de columna
    table_data = [[
        "Material", "Largo (m)", "Unidad Com.", "Cant. Comp.", 
        "Valor Unit. ($)", "Valor Total ($)", "Peso (kg/m)", "Peso Total (kg)"
    ]]
    
    # Obtenemos todos los materiales de la cotización
    materiales = cotizacion.materiales_estructurales.all()
    
    # Calculamos los totales acumulando en cada iteración
    structural_total_value = 0
    structural_total_weight = 0
    
    for material in materiales:
        # Usamos las properties del modelo para los cálculos
        total_value = material.total_value
        total_weight = material.total_weight
        
        structural_total_value += total_value
        structural_total_weight += total_weight
        
        table_data.append([
            material.material_nombre,
            f"{material.largo_m:.2f}",
            f"{material.unidad_comercial:.2f}",
            material.cant_a_comprar,
            f"{material.valor_unitario:,.0f}",
            f"{total_value:,.0f}",
            f"{material.peso_kg_m:.3f}",
            f"{total_weight:.3f}",
        ])
    
    # Fila de totales
    table_data.append([
        "SUBTOTAL ESTRUCTURAL:", '', '', '', '', 
        f"{structural_total_value:,.0f}", 
        "PESO TOTAL:", 
        f"{structural_total_weight:.3f}"
    ])

    # Creamos y estilizamos la tabla
    table = _create_styled_table(
        table_data,
        col_widths=[1.8*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.9*inch, 1.1*inch, 0.8*inch, 1.0*inch],
        subtotal_span=(0, 4)  # Merge primeras 5 columnas en última fila
    )
    
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))


def _build_costs_section(story, cotizacion, styles):
    """
    Construye la tabla de costos adicionales con totales.
    
    Incluye: descripción, unidad, cantidad, valores unitarios y totales.
    """
    story.append(Paragraph("<b>2. Insumos y Costos Adicionales</b>", styles['h2']))
    story.append(Spacer(1, 0.1 * inch))

    # Encabezados
    table_data = [[
        "Descripción / Concepto", "Unidad", "Cantidad", "Valor Unitario ($)", "Valor Total ($)"
    ]]
    
    costos = cotizacion.costos_adicionales.all()
    overhead_total_value = 0
    
    for costo in costos:
        total_value = costo.total_value
        overhead_total_value += total_value
        
        table_data.append([
            costo.descripcion,
            costo.unidad,
            f"{costo.cantidad:.2f}",
            f"{costo.valor_unitario:,.0f}",
            f"{total_value:,.0f}",
        ])
    
    # Fila de subtotal
    table_data.append([
        "SUBTOTAL INSUMOS:", '', '', '', 
        f"{overhead_total_value:,.0f}"
    ])

    table = _create_styled_table(
        table_data,
        col_widths=[2.8*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch],
        subtotal_span=(0, 3)  # Merge primeras 4 columnas en última fila
    )
    
    story.append(table)
    story.append(Spacer(1, 0.5 * inch))


def _build_total_section(story, cotizacion, styles):
    """
    Construye la sección de total general destacada.
    
    Usa el campo total_costo que se guardó al crear la cotización.
    """
    grand_total = cotizacion.total_costo
    
    total_data = [[
        "TOTAL GENERAL DE COSTOS:", f"${grand_total:,.0f}"
    ]]
    
    total_table = Table(total_data, colWidths=[4*inch, 2*inch])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.yellow),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFCC00')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('FONTSIZE', (1, 0), (1, 0), 20),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.red),
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('INNERPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(total_table)
    story.append(Spacer(1, 0.5 * inch))


def _build_notes_section(story, cotizacion, styles):
    """
    Construye la sección de notas internas al final del documento.
    """
    story.append(Paragraph("<b>Notas Internas:</b>", styles['h2']))
    
    if cotizacion.notas_internas:
        # Convertimos saltos de línea a tags HTML para que se muestren correctamente
        formatted_notes = cotizacion.notas_internas.replace('\n', '<br/>')
        story.append(Paragraph(formatted_notes, styles['Normal']))
    else:
        story.append(Paragraph("No se registraron notas internas.", styles['Italic']))


def _create_styled_table(data, col_widths, subtotal_span):
    """
    Crea una tabla estilizada según el diseño corporativo.
    
    Esta función centraliza el estilo de todas las tablas para mantener
    consistencia visual en todo el documento.
    
    Args:
        data: Lista de listas con los datos de la tabla
        col_widths: Lista con anchos de cada columna
        subtotal_span: Tupla (start_col, end_col) para merge en última fila
        
    Returns:
        Table: Objeto Table de ReportLab estilizado
    """
    table = Table(data, colWidths=col_widths)
    
    # Aplicamos estilos comunes a todas las tablas
    table.setStyle(TableStyle([
        # Encabezado: fondo azul oscuro, texto blanco
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002B5B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        
        # Alineación: números a la derecha, texto a la izquierda
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        
        # Tipografía
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Bordes para todas las filas excepto la última (subtotal)
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        
        # Fila de subtotal: fondo gris, texto en negrita
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('SPAN', subtotal_span + (-1, -1)),  # Merge columnas especificadas
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        
        # Destacar columna de total en rojo
        ('TEXTCOLOR', (-1, -1), (-1, -1), colors.red),
    ]))
    
    return table




@login_required
def eliminar_cotizacion(request, cotizacion_id):
    """
    Elimina una cotización después de confirmación del usuario.
    
    Implementa el patrón de confirmación:
    - GET: Muestra página de confirmación
    - POST: Ejecuta la eliminación
    """
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)


    if request.method == "POST":
        # Usuario confirmó: borramos
        # Gracias a on_delete=CASCADE, también se borran los materiales y costos
        cotizacion.delete()
        return redirect(reverse('cotizador_app:cotizaciones'))

    # GET: mostramos confirmación
    return render(request, 'coti_app/eliminar_cotizacion.html', {
        'cotizacion': cotizacion
    })


# ========================================================================
# API JSON ENDPOINTS - Para búsqueda y filtrado en tiempo real
# ========================================================================

@login_required
def cotizacion_search_api(request):
    """
    Endpoint JSON para búsqueda y filtrado de cotizaciones.
    
    Parámetros GET:
        q: Query de búsqueda (busca en proyecto_nombre y cliente__nombre)
        carpeta: Filtro por carpeta específica
        estado: Filtro por estado
    
    Returns:
        JsonResponse con lista de cotizaciones filtradas
    """
    from django.http import JsonResponse
    from django.db.models import Q
    
    # Obtenemos parámetros de búsqueda
    search_query = request.GET.get('q', '').strip()
    carpeta_filter = request.GET.get('carpeta', '').strip()
    estado_filter = request.GET.get('estado', '').strip()
    
    # Query base optimizado
    cotizaciones = Cotizacion.objects.select_related('cliente')\
        .prefetch_related('materiales_estructurales', 'costos_adicionales')\
        .order_by('-fecha_creacion')
    
    # Aplicar filtro de búsqueda (case-insensitive)
    if search_query:
        cotizaciones = cotizaciones.filter(
            Q(proyecto_nombre__icontains=search_query) |
            Q(cliente__nombre__icontains=search_query)
        )
    
    # Filtrar por carpeta
    if carpeta_filter:
        if carpeta_filter == 'sin_carpeta':
            cotizaciones = cotizaciones.filter(carpeta__isnull=True)
        else:
            # Filtrar por nombre de carpeta
            cotizaciones = cotizaciones.filter(carpeta__nombre=carpeta_filter)
    
    # Filtrar por estado
    if estado_filter:
        cotizaciones = cotizaciones.filter(estado=estado_filter)
    
    # Serializar datos a JSON
    data = []
    for cot in cotizaciones:
        data.append({
            'id': cot.id,
            'proyecto_nombre': cot.proyecto_nombre,
            'fecha_creacion': cot.fecha_creacion.strftime('%d-%m-%Y'),
            'total_costo': float(cot.total_costo),
            'cliente_nombre': cot.cliente.nombre if cot.cliente else 'N/A',
            'estado': cot.estado,
            'estado_display': cot.get_estado_display(),
            'carpeta_id': cot.carpeta.id if cot.carpeta else None,
            'carpeta_nombre': cot.carpeta.nombre if cot.carpeta else 'Sin Carpeta',
            # URLs para acciones
            'url_detalle': reverse('cotizador_app:detalle_cotizacion'),
            'url_pdf': reverse('cotizador_app:generar_pdf', args=[cot.id]),
            'url_eliminar': reverse('cotizador_app:eliminar_cotizacion', args=[cot.id]),
        })
    
    return JsonResponse({
        'cotizaciones': data,
        'count': len(data)
    })
