"""
Modelos del sistema de Cotizaciones.

Define las entidades para gestionar cotizaciones, materiales estructurales
y costos adicionales del proyecto.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from usuarios_app.models import Cliente
from .constants import METROS_POR_BARRA  # ✅ FIX MEDIO-003



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


class SeccionMaterial(models.Model):
    """
    Representa una sección o agrupación de materiales dentro de una cotización.
    
    Permite organizar materiales por estructura (ej: "Baño 1", "Habitación Principal", "Techo Galpón").
    Cada cotización puede tener múltiples secciones para mejorar claridad y organización.
    """
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name='secciones',
        verbose_name="Cotización"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Sección",
        help_text="Ej: 'Baño 1', 'Estructura Techo', 'Habitación Principal'"
    )
    
    orden = models.IntegerField(
        default=0,
        verbose_name="Orden de Visualización",
        help_text="Orden en que aparece la sección (menor = primero)"
    )
    
    # Controla si la sección está colapsada en la UI
    colapsada = models.BooleanField(
        default=False,
        verbose_name="Colapsada"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    class Meta:
        verbose_name = "Sección de Materiales"
        verbose_name_plural = "Secciones de Materiales"
        ordering = ['orden', 'id']
        # Evitar secciones duplicadas por nombre en la misma cotización
        unique_together = [['cotizacion', 'nombre']]
    
    def __str__(self):
        return f"{self.nombre} - Cotización #{self.cotizacion.id}"
    
    def clean(self):
        """
        Validación personalizada para SeccionMaterial.
        
        ✅ FIX MEDIO-002: Normaliza el nombre y valida duplicados case-insensitive.
        """
        super().clean()
        
        # Normalizar nombre (capitalizar cada palabra)
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        
        # Verificar duplicados case-insensitive
        duplicados = SeccionMaterial.objects.filter(
            cotizacion=self.cotizacion,
            nombre__iexact=self.nombre
        )
        
        # Excluir la instancia actual si estamos editando
        if self.pk:
            duplicados = duplicados.exclude(pk=self.pk)
        
        if duplicados.exists():
            raise ValidationError({
                'nombre': f'Ya existe una sección con el nombre "{self.nombre}" en esta cotización.'
            })
    
    def save(self, *args, **kwargs):
        """Ejecuta validación automáticamente antes de guardar."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def subtotal_costo(self):
        """Calcula el costo total de todos los materiales en esta sección."""
        return sum(
            material.total_value 
            for material in self.materiales.all()
        )
    
    @property
    def subtotal_peso(self):
        """Calcula el peso total de todos los materiales en esta sección."""
        return sum(
            material.total_weight
            for material in self.materiales.all()
        )


class MaterialEstructural(models.Model):
    """
    Representa un ítem de material estructural dentro de una cotización.
    
    Ejemplos: Vigas H, Perfiles L, Planchas de acero, etc.
    Cada ítem pertenece a una cotización específica y opcionalmente a una sección.
    """
    # on_delete=CASCADE: Si borramos la cotización, borramos todos sus materiales
    cotizacion = models.ForeignKey(
        Cotizacion, 
        on_delete=models.CASCADE, 
        related_name='materiales_estructurales',
        verbose_name="Cotización"
    )
    
    # Relación opcional con sección (null=True permite materiales sin sección asignada)
    seccion = models.ForeignKey(
        'SeccionMaterial',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materiales',
        verbose_name="Sección",
        help_text="Sección a la que pertenece este material (opcional)"
    )
    
    # ID del perfil en la API (para referencia)
    profile_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,  # ✅ FIX ALTO-006: Índice para búsquedas eficientes
        verbose_name="ID Perfil API"
    )
    
    # === Identificación del Material ===
    material_nombre = models.CharField(
        max_length=300,  # ✅ FIX CRÍTICO-004: Aumentado de 150 a 300 para nombres largos
        verbose_name="Material"
    )
    
    # === Largo Requerido ===
    largo_m = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Largo (m)"
    )
    
    # === Unidad Comercial ===
    # Número de barras comerciales (largo_m / 6)
    unidad_comercial = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        verbose_name="U. Comercial",
        help_text="Largo requerido / 6 metros por barra"
    )
    
    # === Cantidad Necesaria ===
    # Redondeo hacia arriba de unidad_comercial
    cant_necesaria = models.IntegerField(
        default=1,
        verbose_name="C. Necesaria",
        help_text="Unidad comercial redondeada hacia arriba"
    )
    
    # === Cantidad a Comprar ===
    # cant_necesaria * 1.25 redondeado hacia arriba (margen de seguridad)
    cant_a_comprar = models.IntegerField(
        default=1,
        verbose_name="A Comprar",
        help_text="Cantidad necesaria × 1.25 (redondeado arriba)"
    )
    
    # === Peso ===
    peso_kg_m = models.DecimalField(
        max_digits=8, 
        decimal_places=3, 
        default=0.000,
        verbose_name="Peso (kg/m)"
    )
    
    # === Valores ===
    # Valor por METRO (no por barra)
    valor_unitario_m = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Valor Unit. ($/m)"
    )
    
    class Meta:
        verbose_name = "Material Estructural"
        verbose_name_plural = "Materiales Estructurales"
        ordering = ['seccion__orden', 'id']
    
    def __str__(self):
        seccion_nombre = self.seccion.nombre if self.seccion else "Sin sección"
        return f"{self.material_nombre} - {seccion_nombre}"
    
    @property
    def peso_total(self):
        """
        Calcula el peso total basado en el LARGO REQUERIDO.
        Esto es para informar al transportista cuánto peso llevar a terreno.
        """
        return float(self.peso_kg_m) * float(self.largo_m)
    
    @property
    def total_value(self):
        """
        Calcula el valor total a facturar.
        Se basa en la cantidad A COMPRAR (incluye margen 25%).
        
        ✅ FIX MEDIO-003: Usa constante METROS_POR_BARRA en lugar de magic number.
        """
        metros_totales_a_comprar = self.cant_a_comprar * float(METROS_POR_BARRA)
        return float(self.valor_unitario_m) * metros_totales_a_comprar
    
    @property
    def total_weight(self):
        """Alias de peso_total para compatibilidad."""
        return self.peso_total


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
    valor_unitario = models.DecimalField(
        max_digits=12,  # ✅ FIX CRÍTICO-004: Aumentado de 10 a 12 para valores grandes
        decimal_places=2,
        default=0.00
    )

    class Meta:
        verbose_name = "Costo Adicional"
        verbose_name_plural = "Costos Adicionales"
    
    @property
    def total_value(self):
        """Calcula el valor total de este costo adicional."""
        return self.cantidad * self.valor_unitario