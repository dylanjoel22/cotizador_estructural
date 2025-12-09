"""
Validadores customizados para el sistema de cotizaciones.

Este módulo contiene validadores reutilizables para campos específicos
del contexto chileno (RUT) y validaciones generales (teléfonos).
"""

import re
from itertools import cycle
from django.core.exceptions import ValidationError


def validar_rut_chileno(rut):
    """
    Valida que el RUT chileno tenga formato correcto y dígito verificador válido.
    
    El RUT es el identificador tributario único en Chile. Usa el algoritmo
    Módulo 11 para verificar que el dígito verificador sea correcto.
    
    Args:
        rut (str): RUT en formato XX.XXX.XXX-X
        
    Raises:
        ValidationError: Si el formato es incorrecto o el DV no coincide
    """
    # Si el campo viene vacío, lo dejamos pasar (Django maneja blank=True en el modelo)
    if not rut:
        return

    # Paso 1: Verificar que tenga el formato estricto chileno
    # Ejemplo válido: 12.345.678-K o 1.234.567-9
    strict_pattern = r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$'
    
    if not re.match(strict_pattern, rut):
        raise ValidationError(
            "El formato del RUT es inválido. Usa el formato: XX.XXX.XXX-X (ejemplo: 12.345.678-K)"
        )

    # Paso 2: Limpiar el RUT (quitamos puntos y guión para trabajar solo con números)
    # Convertimos "12.345.678-K" en "12345678K"
    clean_rut = rut.replace(".", "").replace("-", "").upper()

    # Paso 3: Validar largo razonable
    # Los RUTs válidos tienen entre 2 y 9 caracteres (incluyendo el DV)
    if not (2 <= len(clean_rut) <= 9):
        raise ValidationError("El RUT tiene un largo inválido.")

    # Paso 4: Separar el cuerpo numérico del dígito verificador
    # "12345678K" -> body="12345678", user_dv="K"
    body = clean_rut[:-1]
    user_dv = clean_rut[-1]

    # Paso 5: Aplicar el algoritmo Módulo 11
    # Este algoritmo multiplica cada dígito del RUT (de derecha a izquierda)
    # por una secuencia cíclica [2,3,4,5,6,7,2,3,4...] y suma los resultados
    
    # Convertimos el cuerpo a lista de enteros en orden inverso: [8,7,6,5,4,3,2,1]
    reversed_digits = map(int, reversed(body))
    
    # Creamos un ciclo infinito de factores: 2,3,4,5,6,7,2,3,4,5,6,7...
    factor_cycle = cycle(range(2, 8))
    
    # Multiplicamos cada dígito por su factor y sumamos todo
    # Ejemplo: 8*2 + 7*3 + 6*4 + 5*5 + 4*6 + 3*7 + 2*2 + 1*3
    total_sum = sum(digit * factor for digit, factor in zip(reversed_digits, factor_cycle))
    
    # Calculamos el módulo 11 usando el algoritmo estándar chileno
    # Primero calculamos el resto de dividir total_sum entre 11
    # Luego restamos ese resto de 11
    remainder = 11 - (total_sum % 11)

    # Paso 6: Convertir el resultado a dígito verificador
    # Si el resto es 11, el DV es "0"
    # Si el resto es 10, el DV es "K"
    # De lo contrario, es el número mismo
    if remainder == 11:
        calculated_dv = "0"
    elif remainder == 10:
        calculated_dv = "K"
    else:
        calculated_dv = str(remainder)

    # Paso 7: Comparar el DV calculado con el que ingresó el usuario
    if user_dv != calculated_dv:
        raise ValidationError(
            f"El RUT es inválido. El dígito verificador correcto es '{calculated_dv}', "
            f"pero ingresaste '{user_dv}'."
        )


def validar_telefono(telefono):
    """
    Valida que un número de teléfono tenga una cantidad razonable de dígitos.
    
    Permite caracteres especiales como +, espacios y guiones para facilitar
    el ingreso, pero verifica que la cantidad de números esté entre 8 y 15.
    
    Args:
        telefono (str): Número de teléfono en cualquier formato
        
    Raises:
        ValidationError: Si tiene muy pocos o demasiados dígitos
    """
    if not telefono:
        return

    # Extraemos solo los dígitos numéricos del string
    # "+56 9 1234 5678" se convierte en "56912345678"
    digits_only = re.sub(r'\D', '', telefono)
    
    # Validamos que tenga una cantidad razonable de dígitos
    # 8 es el mínimo (teléfonos fijos chilenos), 15 es el máximo internacional
    if len(digits_only) < 8:
        raise ValidationError("El número de teléfono es demasiado corto (mínimo 8 dígitos).")
    
    if len(digits_only) > 15:
        raise ValidationError("El número de teléfono es demasiado largo (máximo 15 dígitos).")