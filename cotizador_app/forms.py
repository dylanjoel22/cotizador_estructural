from django import forms
from .models import Cotizacion

class CotizacionForm(forms.ModelForm):
    """
    Formulario principal para la Cotización.
    
    Este formulario maneja los campos que se guardan directamente en el modelo Cotizacion.
    Los campos JSONField (`structural_items_json` y `overhead_items_json`) ahora están
    definidos en el modelo y se incluyen aquí como campos ocultos, ya que serán 
    poblados por JavaScript antes de enviar el formulario.
    """
    
    # Los campos JSON se gestionan a través de ModelForm y se fuerzan a HiddenInput en widgets.

    class Meta:
        model = Cotizacion
        fields = [
            'cliente', 
            'proyecto_nombre',
            'notas_internas',
            'total_costo', 
            'structural_items_json',
            'overhead_items_json',
        ]
        
        widgets = {
            'notas_internas': forms.Textarea(attrs={'rows': 4}),
            'structural_items_json': forms.HiddenInput(),
            'overhead_items_json': forms.HiddenInput(),
        }

    # Opcional: Agregar lógica de inicialización o limpieza de datos si es necesario.
    def clean_total_costo(self):
        # Asegura que total_costo no sea nulo, aunque se maneje en JS
        total = self.cleaned_data.get('total_costo')
        if total is None:
            # Coincide con el default=0 del nuevo modelo
            return 0 
        return total
