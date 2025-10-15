from django.shortcuts import render
# Create your views here.

def cotizacion(request):
    return render(request, 'coti_app/cotizacion.html')

def detalle_cotizacion(request):
    return render(request, 'coti_app/detalle_cotizacion.html')


import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse
from .forms import CotizacionForm
from .models import Cotizacion, MaterialEstructural, CostoAdicional
from usuarios_app.models import Cliente 

# Importaciones de ReportLab (Asegúrate de que ReportLab esté instalado: pip install reportlab)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ----------------------------------------------------
# VISTA DE REGISTRO (RENOMBRADA A crear_cotizacion)
# ----------------------------------------------------
def crear_cotizacion(request):
    """
    Maneja la lógica para crear una nueva cotización, guardando la data principal 
    y los ítems estructurales/adicionales, y luego redirige a la generación del PDF.
    """
    error_message = None

    if request.method == 'POST':
        # El formulario CotizacionForm debe estar preparado para recibir los campos
        # estándar y los campos hidden de JSON (structural_items_json, overhead_items_json).
        form = CotizacionForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar la instancia principal de la Cotización
                    cotizacion = form.save(commit=False)
                    cotizacion.save() # Guarda el objeto Cotizacion

                    # 2. Deserializar y guardar los ítems de detalle
                    
                    # Ítems Estructurales
                    structural_data = form.cleaned_data.get('structural_items_json')
                    if structural_data:
                        items = json.loads(structural_data)
                        materiales = [
                            MaterialEstructural(
                                cotizacion=cotizacion,
                                material_nombre=item.get('material_nombre'),
                                largo_mm=item.get('largo_mm'),
                                largo_m=item.get('largo_m'),
                                unidad_comercial=item.get('unidad_comercial'),
                                cant_necesaria=item.get('cant_necesaria'),
                                cant_a_comprar=item.get('cant_a_comprar'),
                                valor_unitario=item.get('valor_unitario'),
                                peso_kg_m=item.get('peso_kg_m'),
                            ) for item in items
                        ]
                        MaterialEstructural.objects.bulk_create(materiales)
                    
                    # Ítems Adicionales
                    overhead_data = form.cleaned_data.get('overhead_items_json')
                    if overhead_data:
                        items = json.loads(overhead_data)
                        costos = [
                            CostoAdicional(
                                cotizacion=cotizacion,
                                descripcion=item.get('descripcion'),
                                unidad=item.get('unidad'),
                                cantidad=item.get('cantidad'),
                                valor_unitario=item.get('valor_unitario'),
                            ) for item in items
                        ]
                        CostoAdicional.objects.bulk_create(costos)

                    # Redirigir a la vista de generación de PDF con el ID de la cotización
                    return redirect(reverse('cotizaciones:generar_pdf', args=[cotizacion.id]))

            except json.JSONDecodeError:
                error_message = "Error: La estructura de datos de costos es inválida."
            except Exception as e:
                error_message = f"Error al guardar la cotización: {e}"
                
        else:
            error_message = "Por favor, corrija los errores del formulario."
            
    else: 
        form = CotizacionForm()
    
    # Asume que el modelo Cliente está disponible para el formulario de selección
    clientes_disponibles = Cliente.objects.all()
    
    context = {
        'form': form,
        'error_message': error_message,
        'clientes_disponibles': clientes_disponibles
    }
    
    # Renderiza la plantilla HTML para ingresar datos
    # NOTA: HE CAMBIADO EL NOMBRE DE LA PLANTILLA A LA QUE HACE REFERENCIA TU ESTRUCTURA
    return render(request, 'coti_app/crear_cotizacion.html', context)


# ----------------------------------------------------
# VISTA PRINCIPAL: GENERACIÓN DE PDF (ReportLab)
# ----------------------------------------------------
def generar_pdf(request, cotizacion_id):
    """
    Genera un PDF con los detalles de la cotización usando ReportLab.
    """
    # 1. Obtener los datos de la cotización
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    
    # Recuperar los ítems de detalle a través de las relaciones
    materiales = cotizacion.materiales_estructurales.all()
    costos = cotizacion.costos_adicionales.all()
    
    # 2. Configurar la respuesta HTTP para el PDF
    response = HttpResponse(content_type='application/pdf')
    # Crea un nombre de archivo amigable
    filename = f"cotizacion_{cotizacion.proyecto_nombre.replace(' ', '_')}_{cotizacion.id}.pdf"
    # El Content-Disposition 'attachment' fuerza la descarga
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # 3. Inicializar el documento ReportLab
    doc = SimpleDocTemplate(
        response, 
        pagesize=letter,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    styles = getSampleStyleSheet()
    Story = [] # Lista para almacenar los elementos del PDF

    # --- 4. Bloque de Información General y Encabezado ---
    Story.append(Paragraph(
        f"<b>REGISTRO DE COSTOS INTERNOS - PROYECTO: {cotizacion.proyecto_nombre.upper()}</b>", 
        styles['Heading1']
    ))
    Story.append(Spacer(1, 0.2 * inch))

    cliente_nombre = cotizacion.cliente.nombre if cotizacion.cliente else "N/A (Sin Cliente Asociado)"
    
    Story.append(Paragraph(f"<b>ID Cotización:</b> {cotizacion.id}", styles['Normal']))
    Story.append(Paragraph(f"<b>Fecha de Registro:</b> {cotizacion.fecha_creacion.strftime('%d-%m-%Y %H:%M')}", styles['Normal']))
    Story.append(Paragraph(f"<b>Cliente:</b> {cliente_nombre}", styles['Normal']))
    Story.append(Spacer(1, 0.1 * inch))


    # --- 5. Tabla de Material Estructural ---
    Story.append(Paragraph("<b>1. Material Estructural (Metales, Planchas, etc.)</b>", styles['h2']))
    Story.append(Spacer(1, 0.1 * inch))

    # Encabezados de la tabla
    data_materiales = [
        ["Material", "Largo (m)", "Unidad Com.", "Cant. Comp.", "Valor Unit. ($)", "Valor Total ($)", "Peso (kg/m)", "Peso Total (kg)"]
    ]
    
    structural_total_value = 0
    structural_total_weight = 0
    
    for item in materiales:
        valor_total = item.cant_a_comprar * item.valor_unitario
        # Cálculo de peso: Cantidad a comprar * Unidad Comercial (metros o unidades) * Peso (kg/m o kg/unidad)
        peso_total = item.cant_a_comprar * item.unidad_comercial * item.peso_kg_m
        
        structural_total_value += valor_total
        structural_total_weight += peso_total
        
        data_materiales.append([
            item.material_nombre,
            f"{item.largo_m:.2f}",
            f"{item.unidad_comercial:.2f}",
            item.cant_a_comprar,
            f"{item.valor_unitario:,.0f}", # Formato sin decimales
            f"{valor_total:,.0f}",
            f"{item.peso_kg_m:.3f}",
            f"{peso_total:.3f}",
        ])
        
    # Fila de Subtotal
    data_materiales.append([
        "SUBTOTAL ESTRUCTURAL:", 
        '', 
        '', 
        '', 
        '', 
        f"{structural_total_value:,.0f}", 
        "PESO TOTAL:", 
        f"{structural_total_weight:.3f}"
    ])

    # Definir el ancho de las columnas (para que quepa en el ancho letter)
    col_widths_materiales = [1.8*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.9*inch, 1.1*inch, 0.8*inch, 1.0*inch]
    
    t_materiales = Table(data_materiales, colWidths=col_widths_materiales)
    t_materiales.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002B5B')), # Encabezado: Azul Oscuro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'), # Valores numéricos a la derecha
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey), # Grid para filas de datos
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey), # Fila de total
        ('SPAN', (0, -1), (4, -1)), # Combinar celdas para el subtotal
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (5, -1), (5, -1), colors.red), # Total en rojo
    ]))
    Story.append(t_materiales)
    Story.append(Spacer(1, 0.3 * inch))

    # --- 6. Tabla de Insumos y Costos Adicionales ---
    Story.append(Paragraph("<b>2. Insumos y Costos Adicionales</b>", styles['h2']))
    Story.append(Spacer(1, 0.1 * inch))

    data_costos = [
        ["Descripción / Concepto", "Unidad", "Cantidad", "Valor Unitario ($)", "Valor Total ($)"]
    ]
    
    overhead_total_value = 0
    
    for item in costos:
        valor_total = item.cantidad * item.valor_unitario
        overhead_total_value += valor_total
        
        data_costos.append([
            item.descripcion,
            item.unidad,
            f"{item.cantidad:.2f}",
            f"{item.valor_unitario:,.0f}",
            f"{valor_total:,.0f}",
        ])
        
    # Fila de Subtotal
    data_costos.append([
        "SUBTOTAL INSUMOS:", 
        '', 
        '', 
        '', 
        f"{overhead_total_value:,.0f}"
    ])

    col_widths_costos = [2.8*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch]
    
    t_costos = Table(data_costos, colWidths=col_widths_costos)
    t_costos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002B5B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('SPAN', (0, -1), (3, -1)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (4, -1), (4, -1), colors.red),
    ]))
    Story.append(t_costos)
    Story.append(Spacer(1, 0.5 * inch))

    # --- 7. Bloque de Totales y Notas ---
    # Nota: El total_costo debe ser calculado y guardado al momento de crear la cotización.
    grand_total = cotizacion.total_costo 
    
    # Tabla para el Total General
    total_data = [
        ["TOTAL GENERAL DE COSTOS:", f"${grand_total:,.0f}"]
    ]
    t_total = Table(total_data, colWidths=[4*inch, 2*inch])
    t_total.setStyle(TableStyle([
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
    Story.append(t_total)
    Story.append(Spacer(1, 0.5 * inch))
    
    # Notas
    Story.append(Paragraph("<b>Notas Internas:</b>", styles['h2']))
    if cotizacion.notas_internas:
        Story.append(Paragraph(cotizacion.notas_internas.replace('\n', '<br/>'), styles['Normal']))
    else:
        Story.append(Paragraph("No se registraron notas internas.", styles['Italic']))

    # 8. Construir el documento y enviarlo en la respuesta
    doc.build(Story)
    return response