from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Profile.

    Convierte las instancias del modelo Profile a JSON y viceversa,
    incluyendo todos los campos del modelo.
    """
    class Meta:
        model = Profile
        fields = '__all__'  # Incluye name, category, y attributes
