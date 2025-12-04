"""
Modelos del sistema de Cotizaciones.

Define las entidades para gestionar cotizaciones, materiales estructurales
y costos adicionales del proyecto.
"""

from django.db import models
from django.utils import timezone
from usuarios_app.models import Cliente


class Cotizacion(models.Model):
    """
    Modelo principal que representa una cotización de proyecto.
    
    Este modelo implementa un patrón dual de almacenamiento:
    1. JSON histórico (structural_items_json, overhead_items_json): Snapshot inmutable
    2. Relaciones FK (materiales_estructurales, costos_adicionales): Datos editables
    
    Esto nos permite mantener un registro exacto de cómo estaba la cotización
    al momento de crearse, mientras permitimos edición futura si es necesario.
    """
    # === Información General ===
    # default=timezone.now guarda la fecha actual al crear (permite modificación manual)
    # auto_now_add=True también guardaría la fecha actual pero NO permite modificación
    fecha_creacion = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Fecha de Creación"
    )
    
    proyecto_nombre = models.CharField(
        max_length=255, 
        verbose_name="Nombre del Proyecto"
    )
    
    # === Relación con Cliente ===
    # on_delete=models.SET_NULL: Si borramos el cliente, la cotización se mantiene
    # Esto es correcto porque las cotizaciones son documentos históricos que deben preservarse
    # incluso si el cliente ya no existe en el sistema
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        related_name='cotizaciones',
        verbose_name="Cliente Asociado"
    )
    
    # === Totales Calculados ===
    # NOTA: Este campo es una desnormalización intencional
    # Guardamos el total para tener un snapshot histórico, pero también
    # podemos calcularlo dinámicamente con la property calculated_total
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

    # === Snapshot JSON ===
    # Estos campos guardan el estado exacto de los ítems al momento de crear la cotización
    # Esto es útil porque:
    # 1. Los precios de materiales pueden cambiar con el tiempo
    # 2. Queremos poder recrear el PDF exactamente igual aunque editemos los ítems
    # 3. Sirve como auditoría histórica
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
        # ordering con '-' ordena descendente (más reciente primero)
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Cotización #{self.id} - {self.proyecto_nombre}"
    
    @property
    def calculated_total(self):
        """
        Calcula el total dinámicamente sumando materiales y costos adicionales.
        
        Este property nos permite obtener el total actualizado si alguien
        editó los ítems desde el admin, sin depender del campo total_costo.
        
        Returns:
            Decimal: Suma total de materiales + costos adicionales
        """
        # Sumamos materiales: cantidad * precio unitario
        materials_total = sum(
            (item.cant_a_comprar * item.valor_unitario) 
            for item in self.materiales_estructurales.all()
        )
        
        # Sumamos costos adicionales: cantidad * precio unitario
        overhead_total = sum(
            (item.cantidad * item.valor_unitario) 
            for item in self.costos_adicionales.all()
        )
        
        return materials_total + overhead_total


class MaterialEstructural(models.Model):
    """
    Representa un ítem de material estructural dentro de una cotización.
    
    Ejemplos: Vigas H, Perfiles L, Planchas de acero, etc.
    Cada ítem pertenece a una cotización específica.
    """
    # on_delete=CASCADE: Si borramos la cotización, borramos todos sus materiales
    # Esto tiene sentido porque un material no puede existir sin su cotización padre
    cotizacion = models.ForeignKey(
        Cotizacion, 
        on_delete=models.CASCADE, 
        related_name='materiales_estructurales'
    )
    
    # === Identificación del Material ===
    material_nombre = models.CharField(max_length=150)
    
    # === Dimensiones ===
    # Guardamos en mm Y en metros para facilitar diferentes cálculos
    largo_mm = models.IntegerField(default=0)
    largo_m = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # === Cantidades ===
    # unidad_comercial: La unidad en que se vende (ej: 6 metros por barra)
    unidad_comercial = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    cant_necesaria = models.IntegerField(default=1)
    cant_a_comprar = models.IntegerField(default=1)  # Puede ser mayor por redondeo comercial
    
    # === Costos y Peso ===
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    peso_kg_m = models.DecimalField(max_digits=8, decimal_places=3, default=0.000)

    class Meta:
        verbose_name = "Material Estructural"
        verbose_name_plural = "Materiales Estructurales"
    
    @property
    def total_value(self):
        """Calcula el valor total de este ítem."""
        return self.cant_a_comprar * self.valor_unitario
    
    @property
    def total_weight(self):
        """Calcula el peso total en kilogramos."""
        return self.cant_a_comprar * self.unidad_comercial * self.peso_kg_m


class CostoAdicional(models.Model):
    """
    Representa costos adicionales a los materiales estructurales.
    
    Ejemplos: Mano de obra, transporte, herramientas, consumibles, etc.
    """
    cotizacion = models.ForeignKey(
        Cotizacion, 
        on_delete=models.CASCADE, 
        related_name='costos_adicionales'
    )
    
    # === Descripción del Costo ===
    descripcion = models.CharField(max_length=200)
    unidad = models.CharField(max_length=50, default='Unidad')
    
    # === Valores ===
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=1.00)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Costo Adicional"
        verbose_name_plural = "Costos Adicionales"
    
    @property
    def total_value(self):
        """Calcula el valor total de este costo adicional."""
        return self.cantidad * self.valor_unitario