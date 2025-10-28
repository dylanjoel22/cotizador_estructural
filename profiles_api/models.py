from django.db import models

class Profile(models.Model):
    """
    Modelo para representar un perfil estructural de acero.

    - 'name' es un identificador único para el perfil (ej. "H 1100x600 596.6").
    - 'category' es el tipo de perfil (ej. "H", "L", "C").
    - 'attributes' es un campo JSON para almacenar propiedades flexibles
      (ej. {"ALTURA_d": 1100, "PESO_KG_M": 596.6, ...}).
    """
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=50, db_index=True)
    attributes = models.JSONField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"