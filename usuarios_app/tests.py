"""
Tests para los validadores customizados del sistema.

Estos tests verifican que los validadores de RUT y teléfono funcionen correctamente
con casos válidos, inválidos y casos borde.s
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from usuarios_app.validators import validar_rut_chileno, validar_telefono


class TestValidadorRUT(TestCase):
    """Tests para el validador de RUT chileno."""
    
    def test_rut_valido_con_k_mayuscula(self):
        """RUT válido con K mayúscula debe pasar."""
        try:
            # RUT válido real: 16.273.816-K
            validar_rut_chileno("16.273.816-K")
        except ValidationError:
            self.fail("RUT válido fue rechazado")
    
    def test_rut_valido_con_k_minuscula(self):
        """RUT válido con k minúscula debe pasar."""
        try:
            # RUT válido real: 16.273.816-k
            validar_rut_chileno("16.273.816-k")
        except ValidationError:
            self.fail("RUT válido fue rechazado")
    
    def test_rut_invalido_digito_verificador_incorrecto(self):
        """RUT con DV incorrecto debe fallar."""
        with self.assertRaises(ValidationError) as context:
            # RUT 24.236.197 tiene DV=K, probamos con 9 (incorrecto)
            validar_rut_chileno("24.236.197-9")
        
        self.assertIn("dígito verificador", str(context.exception))
    
    def test_rut_formato_invalido_sin_puntos(self):
        """RUT sin el formato estricto debe fallar."""
        with self.assertRaises(ValidationError) as context:
            validar_rut_chileno("12345678-K")
        
        self.assertIn("formato", str(context.exception).lower())
    
    def test_rut_vacio_debe_pasar(self):
        """RUT vacío debe ser permitido (blank=True en modelo)."""
        try:
            validar_rut_chileno("")
            validar_rut_chileno(None)
        except ValidationError:
            self.fail("RUT vacío/None no debería lanzar error")
    
    def test_rut_con_caracteres_especiales(self):
        """RUT con caracteres no permitidos debe fallar."""
        with self.assertRaises(ValidationError):
            validar_rut_chileno("12.345.678-K; DROP TABLE clientes;")
    
    def test_rut_demasiado_corto(self):
        """RUT con menos de 2 caracteres debe fallar."""
        with self.assertRaises(ValidationError):
            validar_rut_chileno("1.2-3")
    
    def test_rut_demasiado_largo(self):
        """RUT con más de 9 caracteres (sin formato) debe fallar."""
        with self.assertRaises(ValidationError):
            validar_rut_chileno("123.456.789.012-3")


class TestValidadorTelefono(TestCase):
    """Tests para el validador de teléfono."""
    
    def test_telefono_chileno_valido(self):
        """Teléfono chileno estándar debe pasar."""
        try:
            validar_telefono("+56912345678")
            validar_telefono("912345678")
            validar_telefono("22 123 4567")
        except ValidationError:
            self.fail("Teléfono válido fue rechazado")
    
    def test_telefono_demasiado_corto(self):
        """Teléfono con menos de 8 dígitos debe fallar."""
        with self.assertRaises(ValidationError) as context:
            validar_telefono("1234567")
        
        self.assertIn("demasiado corto", str(context.exception))
    
    def test_telefono_demasiado_largo(self):
        """Teléfono con más de 15 dígitos debe fallar."""
        with self.assertRaises(ValidationError) as context:
            validar_telefono("+123456789012345678")
        
        self.assertIn("demasiado largo", str(context.exception))
    
    def test_telefono_vacio(self):
        """Teléfono vacío debe pasar (blank=True)."""
        try:
            validar_telefono("")
            validar_telefono(None)
        except ValidationError:
            self.fail("Teléfono vacío no debería fallar")
