from django.db.models import F
from django.http import JsonResponse
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
        Busca por el campo 'name' y devuelve resultados formateados.
        Ejemplo: /api/profiles/search/?term=IPE 300
        """
        term = request.query_params.get('term', '').strip()
        if len(term) < 1:
            return Response([])

        # Buscamos perfiles cuyo nombre contenga el término de búsqueda
        profiles = Profile.objects.filter(name__icontains=term)[:15]

        # Formateamos los resultados como se requiere
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
        int_attributes = ['attributes__ALTURA_d', 'attributes__ANCHURA_bf']
        float_attributes = ['attributes__PESO_KG_M']

        for key, value in request.query_params.items():
            if key != 'field' and value:
                if key in int_attributes:
                    try:
                        filters[key] = int(value)
                    except (ValueError, TypeError):
                        return Response({"error": f"Valor inválido para {key}"}, status=400)
                elif key in float_attributes:
                    try:
                        filters[key] = float(value)
                    except (ValueError, TypeError):
                        return Response({"error": f"Valor inválido para {key}"}, status=400)
                else:
                    filters[key] = value
        
        queryset = Profile.objects.filter(**filters)
        values = queryset.values_list(field, flat=True).distinct().order_by(field)
        return Response(list(values))

    @action(detail=False, methods=['get'], url_path='find-unique')
    def find_unique(self, request):
        """
        Encuentra un perfil único basado en la combinación de filtros.
        """
        filters = {}
        int_attributes = ['attributes__ALTURA_d', 'attributes__ANCHURA_bf']
        float_attributes = ['attributes__PESO_KG_M']

        for key, value in request.query_params.items():
            if value:
                if key in int_attributes:
                    try:
                        filters[key] = int(value)
                    except (ValueError, TypeError):
                        return Response({"error": f"Valor inválido para {key}"}, status=400)
                elif key in float_attributes:
                    try:
                        filters[key] = float(value)
                    except (ValueError, TypeError):
                        return Response({"error": f"Valor inválido para {key}"}, status=400)
                else:
                    filters[key] = value

        # Ahora se requieren los 4 filtros
        if not all(k in filters for k in ['category', 'attributes__ALTURA_d', 'attributes__ANCHURA_bf', 'attributes__PESO_KG_M']):
            return Response(None)

        try:
            profile = Profile.objects.get(**filters)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except (Profile.DoesNotExist, Profile.MultipleObjectsReturned):
            return Response(None)