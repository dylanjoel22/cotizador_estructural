from django.db import models
from django.utils import timezone

from usuarios_app.models import Cliente 

# ===============================================
# 1. MODELO PRINCIPAL: Cotizacion
# ===============================================
class Cotizacion(models.Model):
    """
    Representa el registro de una cotización interna o "cruda".
    Contiene la información general, totales, y la serialización de los ítems.
    """
    # Información General
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    proyecto_nombre = models.CharField(max_length=255, verbose_name="Nombre del Proyecto")
    
    # Relación con el Cliente (opcional si el cliente_id puede ser nulo)
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL, # Si el cliente se borra, la cotización mantiene el registro (cliente=null)
        null=True, 
        blank=True, 
        related_name='cotizaciones',
        verbose_name="Cliente Asociado"
    )
    
    # Totales y Notas (Campos de salida del formulario JS)
    total_costo = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        default=0, 
        verbose_name="Costo Total General ($)"
    )
    notas_internas = models.TextField(
        blank=True, 
        verbose_name="Notas Internas"
    )

    # Campos para almacenar los JSON serializados (Si no se quieren guardar como registros individuales)
    # Recomendado para mantener un historial exacto del estado de la cotización al momento de guardar
    structural_items_json = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="JSON Ítems Estructurales"
    )
    overhead_items_json = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="JSON Ítems Adicionales"
    )

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Cotización #{self.id} - {self.proyecto_nombre}"

# ===============================================
# 2. MODELO DE DETALLE: Material Estructural
# (Opcional, si deseas guardar cada ítem en una tabla relacionada)
# ===============================================
class MaterialEstructural(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion, 
        on_delete=models.CASCADE, 
        related_name='materiales_estructurales'
    )
    
    # Campos de Material
    material_nombre = models.CharField(max_length=150)
    largo_mm = models.IntegerField(default=0)
    largo_m = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    unidad_comercial = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    cant_necesaria = models.IntegerField(default=1)
    cant_a_comprar = models.IntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    peso_kg_m = models.DecimalField(max_digits=8, decimal_places=3, default=0.000)

    class Meta:
        verbose_name = "Material Estructural"
        verbose_name_plural = "Materiales Estructurales"

# ===============================================
# 3. MODELO DE DETALLE: Costo Adicional
# ===============================================
class CostoAdicional(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion, 
        on_delete=models.CASCADE, 
        related_name='costos_adicionales'
    )
    
    # Campos de Costo
    descripcion = models.CharField(max_length=200)
    unidad = models.CharField(max_length=50, default='Unidad')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=1.00)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Costo Adicional"
        verbose_name_plural = "Costos Adicionales"