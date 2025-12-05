from django.contrib import admin
from .models import Cotizacion, MaterialEstructural, CostoAdicional, SeccionMaterial

class MaterialEstructuralInline(admin.TabularInline):
    model = MaterialEstructural
    extra = 0

class CostoAdicionalInline(admin.TabularInline):
    model = CostoAdicional
    extra = 0

class SeccionMaterialInline(admin.TabularInline):
    model = SeccionMaterial
    extra = 0
    fields = ('nombre', 'orden', 'colapsada')

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'proyecto_nombre', 'cliente', 'total_costo', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'cliente')
    search_fields = ('proyecto_nombre', 'cliente__nombre')
    inlines = [SeccionMaterialInline, MaterialEstructuralInline, CostoAdicionalInline]

@admin.register(SeccionMaterial)
class SeccionMaterialAdmin(admin.ModelAdmin):
    list_display = ('cotizacion', 'nombre', 'orden', 'colapsada', 'fecha_creacion')
    list_filter = ('cotizacion', 'colapsada')
    search_fields = ('nombre',)
    ordering = ('cotizacion', 'orden')

@admin.register(MaterialEstructural)
class MaterialEstructuralAdmin(admin.ModelAdmin):
    list_display = ('cotizacion', 'seccion', 'material_nombre', 'largo_m', 'cant_a_comprar', 'valor_unitario_m')
    list_filter = ('cotizacion__cliente', 'seccion')
    search_fields = ('material_nombre',)

@admin.register(CostoAdicional)
class CostoAdicionalAdmin(admin.ModelAdmin):
    list_display = ('cotizacion', 'descripcion', 'cantidad', 'valor_unitario')
    list_filter = ('cotizacion__cliente',)
    search_fields = ('descripcion',)
