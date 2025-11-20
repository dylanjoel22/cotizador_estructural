# tu_app/validators.py
import re
from itertools import cycle
from django.core.exceptions import ValidationError

import re
from itertools import cycle
# Nota: La clase ValidationError debe ser importada desde tu framework (ej. Django)
# from django.core.exceptions import ValidationError 

def validar_rut_chileno(rut):
    """
    Valida que el RUT tenga el formato chileno estricto (XX.XXX.XXX-X) 
    y que el dígito verificador sea válido.
    """
    if not rut:
        return # Si es nulo, dejamos que la BD maneje el blank=True

    # NUEVO PASO: 1. Validación Estricta del Formato
    # Requiere: [1-2 digitos] . [3 digitos] . [3 digitos] - [digito o K/k]
    patron_estricto = r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$'

    if not re.match(patron_estricto, rut):
        raise ValidationError("El formato del RUT es inválido. Debe usar el formato estricto: XX.XXX.XXX-X")

    # 2. Limpieza: Eliminamos puntos y guiones, y pasamos a mayúsculas
    # El RUT ingresado ya fue verificado como correcto en su estructura.
    rut_limpio = rut.replace(".", "").replace("-", "").upper()

    # 3. Formato básico: Largo del RUT limpio debe ser entre 2 y 9
    # Un RUT válido limpio tiene entre 2 (1-9) y 9 (29999999-K) caracteres.
    if len(rut_limpio) < 2 or len(rut_limpio) > 9:
        raise ValidationError("El RUT no cumple con el largo mínimo/máximo después de la limpieza.")

    # 4. Separar cuerpo y dígito verificador
    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]

    # 5. Algoritmo Módulo 11 (Lógica matemática)
    reversed_digits = map(int, reversed(cuerpo))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    
    # El uso de (-s) % 11 asegura un resultado positivo entre 0 y 10.
    res = (-s) % 11 

    if res == 10:
        dv_calculado = "K"
    else: # 0, 1, 2, ..., 9
        dv_calculado = str(res)

    # 6. Comparación final
    if dv_ingresado != dv_calculado:
        raise ValidationError(f"El RUT es inválido (Dígito verificador incorrecto. El DV correcto es {dv_calculado}).")

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