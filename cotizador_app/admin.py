from django.contrib import admin
from .models import Cotizacion, MaterialEstructural, CostoAdicional

class MaterialEstructuralInline(admin.TabularInline):
    model = MaterialEstructural
    extra = 0

class CostoAdicionalInline(admin.TabularInline):
    model = CostoAdicional
    extra = 0

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'proyecto_nombre', 'cliente', 'total_costo', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'cliente')
    search_fields = ('proyecto_nombre', 'cliente__nombre')
    inlines = [MaterialEstructuralInline, CostoAdicionalInline]

@admin.register(MaterialEstructural)
class MaterialEstructuralAdmin(admin.ModelAdmin):
    list_display = ('cotizacion', 'material_nombre', 'largo_m', 'cant_a_comprar', 'valor_unitario')
    list_filter = ('cotizacion__cliente',)
    search_fields = ('material_nombre',)

@admin.register(CostoAdicional)
class CostoAdicionalAdmin(admin.ModelAdmin):
    list_display = ('cotizacion', 'descripcion', 'cantidad', 'valor_unitario')
    list_filter = ('cotizacion__cliente',)
    search_fields = ('descripcion',)
