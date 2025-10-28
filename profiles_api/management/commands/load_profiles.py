import json
from django.core.management.base import BaseCommand
from django.conf import settings
from profiles_api.models import Profile

class Command(BaseCommand):
    help = 'Carga perfiles estructurales desde un archivo JSON a la base de datos'

    def handle(self, *args, **options):
        # Ruta al archivo JSON de perfiles
        json_file_path = settings.BASE_DIR / 'perfiles_data.json'

        self.stdout.write(self.style.SUCCESS(f'Iniciando carga de datos desde {json_file_path}'))

        # Limpiar la tabla de perfiles existente para evitar duplicados
        Profile.objects.all().delete()
        self.stdout.write(self.style.WARNING('Se han eliminado los perfiles existentes.'))

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: No se encontró el archivo {json_file_path}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Error: El archivo JSON está mal formado.'))
            return

        profiles_to_create = []
        # Usar un contador para garantizar la unicidad
        for i, item in enumerate(data):
            # Extraer datos comunes y el resto para attributes
            category = item.pop('PREFIJO', None)
            peso = item.get('PESO_KG_M', '')
            altura = item.get('ALTURA_d', '')
            anchura = item.get('ANCHURA_bf', '')

            # Crear un nombre único garantizado con un contador
            name = f"{category} {altura}x{anchura} {peso}kg - ID {i + 1}"

            # Crear instancia del modelo sin guardar aún
            profiles_to_create.append(
                Profile(
                    name=name.strip(),
                    category=category,
                    attributes=item
                )
            )

        # Crear todos los objetos en una sola consulta (bulk_create)
        Profile.objects.bulk_create(profiles_to_create)

        self.stdout.write(self.style.SUCCESS(f'¡Carga completada! Se han añadido {len(profiles_to_create)} perfiles a la base de datos.'))
