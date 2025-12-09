# clientes/forms.py

from django import forms
from .models import Cliente, PersonaContacto # Asegúrate de que este modelo ya no tenga los campos eliminados

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # --- CAMPOS CORREGIDOS ---
        # Solo se listan los campos que SÍ existen en el modelo Cliente (nombre, rut, direccion, ciudad, logo, activo, fecha_registro)
        fields = [
            'nombre', 
            'rut', 
            'codigo_cliente', 
            'telefono', 
            'ciudad', 
            'logo',
            'activo' 
        ] 
        
        widgets = {
            # --- WIDGETS DE TEXTO ---
            'nombre': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'rut': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]',
                                          'placeholder': 'Ejemplo: 12.345.678-K'}),
            'codigo_cliente': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'ciudad': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            
            # --- WIDGET DE ARCHIVO ---
            'logo': forms.ClearableFileInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
            
        }

class PersonaContactoForm(forms.ModelForm):
    class Meta:
        model = PersonaContacto
        exclude = ['cliente']
        # CORRECCIÓN: Removido 'cliente' de fields ya que está en exclude
        # No se puede usar exclude Y fields con el mismo campo
        fields = ['nombre', 'rut', 'email', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'rut': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]',
                                          'placeholder': 'Ejemplo: 12.345.678-K'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
        }