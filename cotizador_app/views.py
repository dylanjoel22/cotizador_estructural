
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse
from .forms import CotizacionForm
from .models import Cotizacion, MaterialEstructural, CostoAdicional
from usuarios_app.models import Cliente
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def cotizacion(request):
    """
    Muestra la lista de cotizaciones existentes.
    """
    cotizaciones = Cotizacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'coti_app/cotizacion.html', {'cotizaciones': cotizaciones})

def detalle_cotizacion(request):
    return render(request, 'coti_app/detalle_cotizacion.html')

def crear_cotizacion(request):
    """
    Maneja la lógica para crear una nueva cotización.
    """
    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    cotizacion = form.save()

                    structural_data = form.cleaned_data.get('structural_items_json')
                    if structural_data:
                        for item in structural_data:
                            MaterialEstructural.objects.create(
                                cotizacion=cotizacion,
                                material_nombre=item.get('material_nombre'),
                                largo_mm=item.get('largo_mm'),
                                largo_m=item.get('largo_m'),
                                unidad_comercial=item.get('unidad_comercial'),
                                cant_necesaria=item.get('cant_necesaria'),
                                cant_a_comprar=item.get('cant_a_comprar'),
                                valor_unitario=item.get('valor_unitario'),
                                peso_kg_m=item.get('peso_kg_m'),
                            )

                    overhead_data = form.cleaned_data.get('overhead_items_json')
                    if overhead_data:
                        for item in overhead_data:
                            CostoAdicional.objects.create(
                                cotizacion=cotizacion,
                                descripcion=item.get('descripcion'),
                                unidad=item.get('unidad'),
                                cantidad=item.get('cantidad'),
                                valor_unitario=item.get('valor_unitario'),
                            )
                    
                    return redirect(reverse('cotizador_app:cotizaciones'))

            except json.JSONDecodeError:
                error_message = "Error: La estructura de datos de costos es inválida."
            except Exception as e:
                error_message = f"Error al guardar la cotización: {e}"
        else:
            error_message = "Por favor, corrija los errores del formulario."
    else:
        form = CotizacionForm()
        error_message = None

    clientes_disponibles = Cliente.objects.all()
    
    context = {
        'form': form,
        'error_message': error_message,
        'clientes_disponibles': clientes_disponibles
    }
    
    return render(request, 'coti_app/crear_cotizacion.html', context)


def generar_pdf(request, cotizacion_id):
    """
    Genera un PDF con los detalles de la cotización usando ReportLab.
    """
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    materiales = cotizacion.materiales_estructurales.all()
    costos = cotizacion.costos_adicionales.all()
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"cotizacion_{cotizacion.proyecto_nombre.replace(' ', '_')}_{cotizacion.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(
        response, 
        pagesize=letter,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    styles = getSampleStyleSheet()
    Story = []

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

    Story.append(Paragraph("<b>1. Material Estructural (Metales, Planchas, etc.)</b>", styles['h2']))
    Story.append(Spacer(1, 0.1 * inch))

    data_materiales = [
        ["Material", "Largo (m)", "Unidad Com.", "Cant. Comp.", "Valor Unit. ($)", "Valor Total ($)", "Peso (kg/m)", "Peso Total (kg)"]
    ]
    
    structural_total_value = 0
    structural_total_weight = 0
    
    for item in materiales:
        valor_total = item.cant_a_comprar * item.valor_unitario
        peso_total = item.cant_a_comprar * item.unidad_comercial * item.peso_kg_m
        
        structural_total_value += valor_total
        structural_total_weight += peso_total
        
        data_materiales.append([
            item.material_nombre,
            f"{item.largo_m:.2f}",
            f"{item.unidad_comercial:.2f}",
            item.cant_a_comprar,
            f"{item.valor_unitario:,.0f}",
            f"{valor_total:,.0f}",
            f"{item.peso_kg_m:.3f}",
            f"{peso_total:.3f}",
        ])
        
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

    col_widths_materiales = [1.8*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.9*inch, 1.1*inch, 0.8*inch, 1.0*inch]
    
    t_materiales = Table(data_materiales, colWidths=col_widths_materiales)
    t_materiales.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002B5B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('SPAN', (0, -1), (4, -1)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (5, -1), (5, -1), colors.red),
    ]))
    Story.append(t_materiales)
    Story.append(Spacer(1, 0.3 * inch))

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

    grand_total = cotizacion.total_costo 
    
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
    
    Story.append(Paragraph("<b>Notas Internas:</b>", styles['h2']))
    if cotizacion.notas_internas:
        Story.append(Paragraph(cotizacion.notas_internas.replace('\n', '<br/>'), styles['Normal']))
    else:
        Story.append(Paragraph("No se registraron notas internas.", styles['Italic']))

    doc.build(Story)
    return response

def eliminar_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)

    # Si el usuario ya confirmó (POST), se borra
    if request.method == "POST":
        cotizacion.delete()
        return redirect(reverse('cotizador_app:cotizaciones'))

    # Si entra por GET, mostrar confirmación automática
    return render(request, 'coti_app/eliminar_cotizacion.html', {
        'cotizacion': cotizacion
    })