import os
import django
import json

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
django.setup()

# 2. Importar tu modelo (Asegúrate que 'usuarios_app' sea el nombre correcto de tu app)
from profiles_api.models import Profile 

def cargar_datos():
    ruta_archivo = 'perfiles_backup_oficial.json'
    
    print(f"Leyendo archivo {ruta_archivo}...")
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        print(f"Se encontraron {len(datos)} perfiles. Iniciando carga...")
        
        contador = 0
        for item in datos:
            # 3. Construir el nombre único (Ej: "H 1100x600 596.6")
            # Usamos get() por si algún dato viene vacío para que no falle
            prefijo = item.get('PREFIJO', 'X')
            alto = item.get('ALTURA_d', 0)
            ancho = item.get('ANCHURA_bf', 0)
            peso = item.get('PESO_KG_M', 0)
            
            nombre_generado = f"{prefijo} {alto}x{ancho} {peso}"
            
            # 4. Guardar en la base de datos
            # update_or_create sirve para: Si existe lo actualiza, si no, lo crea.
            obj, created = Profile.objects.update_or_create(
                name=nombre_generado,
                defaults={
                    'category': prefijo,
                    'attributes': item  # <--- AQUÍ ESTÁ LA MAGIA: Guardamos todo el JSON
                }
            )
            
            contador += 1
            if contador % 100 == 0:
                print(f"Procesados {contador} perfiles...")

        print(f"¡ÉXITO! Se han cargado/actualizado {contador} perfiles correctamente.")

    except FileNotFoundError:
        print("ERROR: No encuentro el archivo 'perfiles_backup_oficial.json'.")
    except Exception as e:
        print(f"ERROR: Ocurrió un fallo: {e}")

if __name__ == '__main__':
    cargar_datos()