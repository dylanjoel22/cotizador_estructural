# clientes/forms.py

from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # Se añade 'empresa' a la lista de campos (asumiendo que lo necesitas)
        fields = [
            'nombre', 'rut', 'persona_contacto', 
            'empresa', 'telefono', 'email', 
            'direccion', 'ciudad', 'logo'
        ] 
        
        widgets = {
            # --- WIDGETS DE TEXTO ---
            'nombre': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'rut': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'persona_contacto': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            
            # ¡NUEVO WIDGET para 'empresa'!
            'empresa': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            
            'telefono': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'direccion': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            'ciudad': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-[#7CA8D5] focus:border-[#7CA8D5]'}),
            
            # --- WIDGET DE ARCHIVO ---
            'logo': forms.ClearableFileInput(attrs={
                # Estilos de Tailwind para el input de tipo file
                'class': 'w-full p-2 border border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
        }