from django.db import models
from .validators import validar_rut_chileno, validar_telefono

class Cliente(models.Model):
    # Identificación Primaria
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre o Razón Social")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT", help_text="Formato: XX.XXX.XXX-X", blank=True, null=True,validators=[validar_rut_chileno])
    codigo_cliente = models.CharField(max_length=20, unique=True, verbose_name="Código de Cliente", blank=True, null=True)

    # Información de Contacto
    telefono = models.CharField(max_length=20, blank=True, null=True, validators=[validar_telefono])

    # Información de Dirección
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    
    # Campos de control
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # Se guarda en 'media/clientes_logos/' y es opcional (blank=True, null=True)
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
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    
    def clean(self):
        """
        Este método se llama automáticamente al guardar desde el Admin de Django.
        Es el lugar perfecto para 'arreglar' datos antes de guardarlos.
        """
        super().clean() # Mantiene las validaciones estándar
        
        if self.rut:
            # Estandarizar el RUT: Siempre guardar en mayúsculas
            self.rut = self.rut.upper()
            
            # Opcional: Si quieres guardar siempre SIN puntos y CON guión, podrías formatearlo aquí.
            # Por ejemplo, convertir 12.345.678-k a 12345678-K


class PersonaContacto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT", help_text="Formato: XX.XXX.XXX-X", blank=True, null=True,validators=[validar_rut_chileno])
    email = models.EmailField(max_length=100, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, verbose_name="Número de Teléfono", validators=[validar_telefono])
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contactos', verbose_name="Empresa Asociada")

    class Meta:
        verbose_name = "Persona de Contacto"
        verbose_name_plural = "Personas de Contacto"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.cliente.nombre})"