"""
Constantes de negocio para el sistema de cotizaciones.

Centraliza valores que se usan en cálculos de materiales y costos,
facilitando el mantenimiento y permitiendo ajustes futuros.
"""

from decimal import Decimal

# ✅ FIX MEDIO-003: Constante para largo estándar de barra comercial
METROS_POR_BARRA = Decimal('6.0')

# ✅ FIX MEDIO-004: Constante para margen de seguridad en compras
MARGEN_SEGURIDAD = Decimal('1.25')  # 25% de margen
