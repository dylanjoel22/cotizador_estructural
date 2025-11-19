# tu_app/validators.py
import re
from itertools import cycle
from django.core.exceptions import ValidationError

def validar_rut_chileno(rut):
    """
    Valida que el RUT tenga el formato correcto y que el dígito verificador sea válido.
    Acepta formatos: 12.345.678-9 o 12345678-9 (con o sin puntos).
    """
    if not rut:
        return # Si es nulo, dejamos que la BD maneje el blank=True

    # 1. Limpieza: Eliminamos puntos y guiones, y pasamos a mayúsculas
    rut_limpio = rut.replace(".", "").replace("-", "").upper()

    # 2. Formato básico: Debe tener largo mínimo y ser alfanumérico
    if len(rut_limpio) < 2 or not re.match(r'^[0-9]+[0-9K]$', rut_limpio):
        raise ValidationError("El formato del RUT no es válido. Use: XX.XXX.XXX-X")

    # 3. Separar cuerpo y dígito verificador
    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]

    # 4. Algoritmo Módulo 11 (Lógica matemática)
    reversed_digits = map(int, reversed(cuerpo))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    res = (-s) % 11

    if res == 10:
        dv_calculado = "K"
    elif res == 11: # Matemáticamente el mod 11 no da 11, pero en la lógica RUT, si el resto es 0, el DV es 0.
        dv_calculado = "0" 
    else:
        dv_calculado = str(res)

    # 5. Comparación final
    if dv_ingresado != dv_calculado:
        raise ValidationError(f"El RUT es inválido (Dígito verificador incorrecto).")

def validar_telefono(telefono):
    """
    Valida que el teléfono tenga entre 8 y 15 dígitos.
    Permite caracteres como +, espacios y guiones, pero verifica que haya números suficientes.
    """
    if not telefono:
        return

    # Quitamos caracteres no numéricos para contar
    numeros = re.sub(r'\D', '', telefono)
    
    if len(numeros) < 8:
        raise ValidationError("El número de teléfono es demasiado corto.")
    if len(numeros) > 15:
        raise ValidationError("El número de teléfono es demasiado largo.")