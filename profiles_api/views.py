from django.db.models import F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet que proporciona acciones de CRUD completas para el modelo Profile
    y endpoints personalizados para búsqueda y filtros.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Autocompletado para búsqueda experta.
        """
        term = request.query_params.get('term', '').strip()
        if len(term) < 1:
            return Response([])

        profiles = Profile.objects.filter(name__icontains=term)[:15]

        results = [
            {
                "id": p.id,
                "text": f"{p.name} | {p.attributes.get('ALTURA_d', 'N/A')}x{p.attributes.get('ANCHURA_bf', 'N/A')} mm | {p.attributes.get('PESO_KG_M', 'N/A')} kg/m"
            }
            for p in profiles
        ]
        return Response(results)

    @action(detail=False, methods=['get'], url_path='get-options')
    def get_options(self, request):
        """
        Obtiene listas de opciones para los filtros dependientes.
        """
        field = request.query_params.get('field')
        if not field:
            return Response({"error": "El parámetro 'field' es requerido."}, status=400)

        filters = {}
        # Campos que sabemos que son numéricos en el JSON
        int_attributes = ['attributes__ALTURA_d', 'attributes__ANCHURA_bf']
        float_attributes = ['attributes__PESO_KG_M']

        for key, value in request.query_params.items():
            if key != 'field' and value:
                try:
                    if key in int_attributes:
                        filters[key] = int(float(value)) # float primero por seguridad (ej: "100.0")
                    elif key in float_attributes:
                        filters[key] = float(value)
                    else:
                        filters[key] = value
                except (ValueError, TypeError):
                    continue # Si falla un filtro, lo ignoramos en vez de romper todo
        
        queryset = Profile.objects.filter(**filters)
        values = queryset.values_list(field, flat=True).distinct().order_by(field)
        return Response(list(values))

    @action(detail=False, methods=['get'], url_path='find-unique')
    def find_unique(self, request):
        """
        Encuentra un perfil único basado en la combinación de filtros.
        CORREGIDO: Manejo robusto de tipos de datos (Str -> Int/Float).
        """
        # 1. Obtener parámetros individualmente para mayor control
        category = request.query_params.get('category')
        altura = request.query_params.get('attributes__ALTURA_d')
        ancho = request.query_params.get('attributes__ANCHURA_bf')
        peso = request.query_params.get('attributes__PESO_KG_M')

        # 2. Si falta algún dato, no buscamos nada
        if not all([category, altura, ancho, peso]):
            return Response(None)

        try:
            # 3. CONVERSIÓN DE TIPOS (La parte crítica)
            # Django recibe "1000" (str) pero el JSON tiene 1000 (int). Debemos convertir.
            
            # Convertimos a float primero para manejar strings como "1000.0"
            altura_val = float(altura)
            ancho_val = float(ancho)
            peso_val = float(peso)

            # Si es un número entero (ej: 1000.0), lo pasamos a int (1000)
            # Esto es vital porque en el JSON: 1000 != 1000.0 en búsquedas exactas a veces
            if altura_val.is_integer(): altura_val = int(altura_val)
            if ancho_val.is_integer(): ancho_val = int(ancho_val)
            
            # 4. Query Segura
            # Usamos filter().first() en lugar de get().
            # get() lanza error si hay 0 resultados o si hay 2 resultados. first() devuelve None (seguro).
            profile = Profile.objects.filter(
                category=category,
                attributes__ALTURA_d=altura_val,
                attributes__ANCHURA_bf=ancho_val,
                attributes__PESO_KG_M=peso_val
            ).first()

            if profile:
                serializer = self.get_serializer(profile)
                return Response(serializer.data)
            else:
                return Response(None)

        except (ValueError, TypeError) as e:
            # Si los datos no son números válidos, retornamos null silenciosamente
            print(f"Error de conversión en find_unique: {e}")
            return Response(None)
        except Exception as e:
            print(f"Error inesperado en find_unique: {e}")
            return Response(None)