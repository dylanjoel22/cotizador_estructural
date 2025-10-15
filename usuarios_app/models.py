from django.db import models

class Cliente(models.Model):
    # Identificación Primaria
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre o Razón Social")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT", help_text="Formato: XX.XXX.XXX-X", blank=True, null=True)
    
    # Información de Contacto
    persona_contacto = models.CharField(max_length=100, verbose_name="Persona de Contacto", blank=True, null=True)
    empresa = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)

    # Información de Dirección (Domicilio Fiscal/Comercial)
    direccion = models.CharField(max_length=255, verbose_name="Dirección Comercial", blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    
    # Campos de control
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # NUEVO CAMPO PARA EL LOGO
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