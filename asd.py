import json
# CAMBIA ESTO por tu importación real
from profiles_api.models import Profile

# Abre el archivo
with open('perfiles_data.json', encoding='utf-8') as f:
    datos = json.load(f)

    # Recorre la lista y crea los objetos
    for item in datos:
        # Aquí asumo que las llaves del JSON se llaman igual que los campos de tu modelo
        # Si no, tienes que mapearlos: campo_modelo=item['campo_json']
        Cotizacion.objects.create(**item) 

print("¡Datos cargados exitosamente!")