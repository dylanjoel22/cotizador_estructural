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
        fields = ['id', 'name', 'category', 'attributes']  # ✅ FIX MEDIO-007: Explícito en lugar de '__all__'
