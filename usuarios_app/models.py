"""
Modelos de gestión de Clientes y Contactos.

Define las entidades principales para el manejo de empresas cliente
y sus personas de contacto asociadas.
"""

from django.db import models
from .validators import validar_rut_chileno, validar_telefono


class Cliente(models.Model):
    """
    Modelo que representa una empresa cliente.
    
    Almacena información de identificación, contacto y control operativo
    de las empresas que contratan nuestros servicios.
    """
    # === Identificación Primaria ===
    # unique=True asegura que no haya duplicados en la base de datos
    nombre = models.CharField(
        max_length=200, 
        unique=True, 
        verbose_name="Nombre o Razón Social"
    )
    
    # validators=[...] ejecuta funciones de validación antes de guardar
    # blank=True permite formularios vacíos, null=True permite NULL en BD
    rut = models.CharField(
        max_length=15, 
        unique=True, 
        verbose_name="RUT", 
        help_text="Formato: XX.XXX.XXX-X", 
        blank=True, 
        null=True,
        validators=[validar_rut_chileno]
    )
    
    codigo_cliente = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Código de Cliente", 
        blank=True, 
        null=True
    )

    # === Información de Contacto ===
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        validators=[validar_telefono]
    )

    # === Información de Dirección ===
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    
    # === Campos de Control ===
    # BooleanField con default=True facilita marcar clientes como inactivos sin borrarlos
    activo = models.BooleanField(default=True)
    
    # auto_now_add=True guarda automáticamente la fecha al crear el registro (no se puede modificar)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # === Logo de la Empresa ===
    # upload_to define la subcarpeta dentro de MEDIA_ROOT donde se guardarán los archivos
    # Esto nos permite tener logos organizados en media/clientes_logos/
    logo = models.ImageField(
        upload_to='clientes_logos/', 
        blank=True, 
        null=True, 
        verbose_name="Logo de la Empresa (Opcional)",
        help_text="Se usará en la cotización si está disponible."
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        # ordering define el orden por defecto en queries (útil para select dropdowns)
        ordering = ['nombre']

    def __str__(self):
        """
        Representación en string del objeto.
        Se usa en el admin de Django y en cualquier lugar donde se imprima el objeto.
        """
        return self.nombre
    
    def clean(self):
        """
        Hook de validación que se ejecuta antes de guardar.
        
        Django llama a este método automáticamente cuando guardas desde el Admin
        o cuando llamas a full_clean() manualmente. Es el lugar ideal para
        normalizar datos o aplicar validaciones complejas que involucran múltiples campos.
        """
        super().clean()  # Mantiene las validaciones estándar de Django
        
        # Normalizamos el RUT a mayúsculas para consistencia en la BD
        # Esto garantiza que "12.345.678-k" y "12.345.678-K" se guarden igual
        if self.rut:
            self.rut = self.rut.upper()


class PersonaContacto(models.Model):
    """
    Modelo que representa una persona de contacto asociada a un Cliente.
    
    Cada persona pertenece a una empresa (Cliente) y tiene sus propios datos
    de identificación y contacto.
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    
    rut = models.CharField(
        max_length=15, 
        unique=True,  # Cada persona tiene un RUT único en todo el sistema
        verbose_name="RUT", 
        help_text="Formato: XX.XXX.XXX-X", 
        blank=True, 
        null=True,
        validators=[validar_rut_chileno]
    )
    
    email = models.EmailField(max_length=100, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, verbose_name="Número de Teléfono", validators=[validar_telefono])
    
    # === Foreign Key: La Relación con Cliente ===
    # ✅ FIX ALTO-005: on_delete=PROTECT evita borrado accidental de clientes con contactos
    # Si intentas borrar un Cliente que tiene PersonasContacto, Django lanzará un error
    # Esto es más seguro que CASCADE, que borra todos los contactos sin confirmación
    # 
    # Alternativas de on_delete:
    # - CASCADE: Borraría automáticamente los contactos (PELIGROSO - evitado)
    # - SET_NULL: Pondría cliente=null si se borra el cliente (requiere null=True)
    # - SET_DEFAULT: Asignaría un valor por defecto (requiere default=...)
    #
    # related_name='contactos': Permite hacer cliente.contactos.all() en vez de cliente.personacontacto_set.all()
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT,  # ✅ Cambiado de CASCADE a PROTECT
        related_name='contactos', 
        verbose_name="Empresa Asociada"
    )

    class Meta:
        verbose_name = "Persona de Contacto"
        verbose_name_plural = "Personas de Contacto"
        ordering = ['nombre']

    def __str__(self):
        """
        Mostramos el nombre de la persona y su empresa asociada.
        Ejemplo: "Juan Pérez (Empresa ABC S.A.)"
        """
        return f"{self.nombre} ({self.cliente.nombre})"