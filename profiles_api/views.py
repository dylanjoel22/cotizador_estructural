"""
API ViewSet para gestión de Perfiles Estructurales.

Este módulo proporciona endpoints RESTful para consultar perfiles de acero
con filtros avanzados y búsqueda por autocompletado.
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Profile
from .serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet que proporciona operaciones CRUD y endpoints personalizados.
    
    Un ViewSet en Django REST Framework es una clase que combina la lógica
    de múltiples vistas relacionadas (list, create, retrieve, update, delete).
    
    Endpoints estándar (generados automáticamente):
    - GET /api/profiles/ -> list()
    - POST /api/profiles/ -> create()
    - GET /api/profiles/{id}/ -> retrieve()
    - PUT/PATCH /api/profiles/{id}/ -> update()
    - DELETE /api/profiles/{id}/ -> destroy()
    
    Endpoints personalizados (definidos con @action):
    - GET /api/profiles/search/?term=xxx -> search()
    - GET /api/profiles/get-options/?field=xxx -> get_options()
    - etc.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # ✅ FIX CRÍTICO-001


    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Endpoint de autocompletado para búsqueda rápida de perfiles.
        
        El decorador @action nos permite crear endpoints custom.
        - detail=False: No requiere ID en la URL (/search/ en vez de /{id}/search/)
        - methods=['get']: Solo acepta peticiones GET
        - url_path='search': Define el path del endpoint
        
        Uso: GET /api/profiles/search/?term=H%201100
        """
        term = request.query_params.get('term', '').strip()
        
        # Validación: necesitamos al menos 1 carácter para buscar
        if len(term) < 1:
            return Response([])

        # Búsqueda case-insensitive limitada a 15 resultados
        # OPTIMIZACIÓN: [:15] limita en la BD, no en Python (más eficiente)
        profiles = Profile.objects.filter(name__icontains=term)[:15]

        # Formatearmos los resultados para el plugin select2 de jQuery
        # Requiere estructura: [{"id": 1, "text": "H 1100x600 | ..."}, ...]
        results = [
            {
                "id": profile.id,
                "text": f"{profile.name} | {profile.attributes.get('ALTURA_d', 'N/A')}x"
                        f"{profile.attributes.get('ANCHURA_bf', 'N/A')} mm",
                "tf": profile.attributes.get('DIMENSION_tf'),
                "tw": profile.attributes.get('DIMENSION_tw')
            }
            for profile in profiles
        ]
        
        return Response(results)

    @action(detail=False, methods=['get'], url_path='get-options')
    def get_options(self, request):
        """
        Obtiene valores únicos de un campo para poblar dropdowns dependientes.
        
        Este endpoint permite filtros en cascada. Por ejemplo:
        1. Usuario selecciona category="H"
        2. Frontend llama: /get-options/?field=attributes__ALTURA_d&category=H
        3. Retorna solo las alturas disponibles para perfiles H
        
        Uso: GET /api/profiles/get-options/?field=attributes__ALTURA_d&category=H
        """
        field = request.query_params.get('field')
        
        if not field:
            return Response({"error": "El parámetro 'field' es requerido."}, status=400)

        # Construimos filtros dinámicamente basados en los query params
        filters = self._build_filters_from_params(request.query_params, exclude_key='field')
        
        # Aplicamos filtros y obtenemos valores únicos del campo solicitado
        queryset = Profile.objects.filter(**filters)
        values = queryset.values_list(field, flat=True).distinct().order_by(field)
        
        return Response(list(values))

    @action(detail=False, methods=['get'], url_path='find-unique')
    def find_unique(self, request):
        """
        Encuentra un perfil único basado en la combinación exacta de parámetros.
        
        Este endpoint se usa cuando el usuario selecciona todos los filtros
        y queremos cargar los datos completos del perfil coincidente.
        
        IMPORTANTE: Usamos .first() en vez de .get() porque:
        - .get() lanza excepción si no encuentra (DoesNotExist) o si encuentra múltiples (MultipleObjectsReturned)
        - .first() retorna None si no encuentra, o el primer resultado si hay múltiples
        - Esto hace el endpoint más robusto y fácil de usar desde JavaScript
        """
        # Extraemos parámetros de búsqueda
        category = request.query_params.get('category')
        altura = request.query_params.get('attributes__ALTURA_d')
        ancho = request.query_params.get('attributes__ANCHURA_bf')
        tf = request.query_params.get('attributes__DIMENSION_tf')
        tw = request.query_params.get('attributes__DIMENSION_tw')
        
        # Validamos que tengamos todos los datos necesarios
        if not all([category, altura, ancho, tf, tw]):
            return Response(None)

        try:
            # Convertimos strings a números (ver método helper más abajo)
            altura_val = self._convert_to_numeric(altura)
            ancho_val = self._convert_to_numeric(ancho)
            tf_val = self._convert_to_numeric(tf)
            tw_val = self._convert_to_numeric(tw)
            
            # Buscamos el perfil con todos los parámetros
            profile = Profile.objects.filter(
                category=category,
                attributes__ALTURA_d=altura_val,
                attributes__ANCHURA_bf=ancho_val,
                attributes__DIMENSION_tf=tf_val,
                attributes__DIMENSION_tw=tw_val
            ).first()

            if profile:
                serializer = self.get_serializer(profile)
                return Response(serializer.data)
            else:
                return Response(None)

        except (ValueError, TypeError) as e:
            # Error de conversión: datos inválidos del frontend
            return Response(None)

    @action(detail=False, methods=['get'], url_path='get-thickness-combinations')
    def get_thickness_combinations(self, request):
        """
        Retorna combinaciones únicas de espesores de ala (tf) y alma (tw).
        
        Se usa cuando el usuario ya seleccionó categoría, altura y ancho,
        y queremos mostrarle las combinaciones de espesores disponibles.
        
        Ejemplo de respuesta:
        [
            {"tf": 28, "tw": 16},
            {"tf": 24, "tw": 14},
            ...
        ]
        """
        category = request.query_params.get('category')
        height = request.query_params.get('height')
        width = request.query_params.get('width')
        
        # Convertimos los valores numéricos
        try:
            if height:
                height = self._convert_to_numeric(height)
            if width:
                width = self._convert_to_numeric(width)
        except (ValueError, TypeError):
            # Si hay error de conversión, retornamos lista vacía
            return Response([])

        # Filtramos y obtenemos combinaciones únicas de espesores
        queryset = Profile.objects.filter(
            category=category,
            attributes__ALTURA_d=height,
            attributes__ANCHURA_bf=width
        ).values('attributes__DIMENSION_tf', 'attributes__DIMENSION_tw').distinct()
        
        # Formateamos la respuesta
        data = [
            {
                'tf': item['attributes__DIMENSION_tf'],  # Espesor de ala
                'tw': item['attributes__DIMENSION_tw']   # Espesor de alma
            }
            for item in queryset
        ]
        
        # Ordenamos por espesor de ala descendente (más grueso primero)
        # Usamos lambda con None-safe para evitar errores si hay valores null
        data.sort(key=lambda x: x['tf'] if x['tf'] is not None else 0, reverse=True)
        
        return Response(data)
    
    # ========================================================================
    # MÉTODOS HELPER PRIVADOS (no son endpoints)
    # ========================================================================
    
    @staticmethod
    def _convert_to_numeric(value):
        """
        Convierte un string a int o float según corresponda.
        
        Este método centraliza la lógica de conversión que estaba duplicada
        en múltiples endpoints. Maneja casos como:
        - "1000" -> 1000 (int)
        - "1000.0" -> 1000 (int, porque .0 es redundante)
        - "1000.5" -> 1000.5 (float)
        
        PROBLEMA QUE RESUELVE:
        JavaScript envía números como strings en URLs. Pero en nuestra BD,
        los campos JSON tienen tipos nativos (int/float). Si comparamos
        "1000" (str) con 1000 (int), la base de datos no encuentra coincidencias.
        
        Args:
            value: String a convertir
            
        Returns:
            int o float según el valor
            
        Raises:
            ValueError: Si el string no representa un número válido
        """
        float_val = float(value)
        
        # Si el número es entero (ej: 1000.0), lo retornamos como int
        # Esto es importante para que coincida con el tipo en la BD
        if float_val.is_integer():
            return int(float_val)
        
        return float_val
    
    def _build_filters_from_params(self, query_params, exclude_key=None):
        """
        Construye un diccionario de filtros desde los query parameters.
        
        Centraliza la lógica de conversión de tipos para evitar duplicación.
        
        Args:
            query_params: QueryDict de Django con parámetros de la URL
            exclude_key: Key a excluir del resultado (ej: 'field')
            
        Returns:
            dict: Filtros listos para usar en .filter(**filters)
        """
        # Definimos qué campos deben convertirse a qué tipo
        # Esto lo sabemos por la estructura del JSON en la BD
        int_attributes = ['attributes__ALTURA_d', 'attributes__ANCHURA_bf']
        float_attributes = ['attributes__PESO_KG_M']
        
        filters = {}
        
        for key, value in query_params.items():
            # Saltamos el key a excluir y valores vacíos
            if key == exclude_key or not value:
                continue
            
            try:
                # Aplicamos conversión según el tipo esperado
                if key in int_attributes:
                    filters[key] = int(float(value))  # float() primero por seguridad
                elif key in float_attributes:
                    filters[key] = float(value)
                else:
                    # Para strings (como category), usamos el valor directo
                    filters[key] = value
            except (ValueError, TypeError):
                # Si un filtro es inválido, lo ignoramos en vez de romper todo
                continue
        
        return filters