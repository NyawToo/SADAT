from django.contrib import admin
from .models import MicroempresaIntegral, MicroempresaSatelite, ProductoTerminado, CategoriaProducto, Servicio
from .models_materia_prima import MateriaPrima, CategoriaMateriaPrima, MovimientoMateriaPrima

@admin.register(MicroempresaIntegral)
class MicroempresaIntegralAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'rut_empresa', 'usuario')
    search_fields = ('nombre_empresa', 'rut_empresa')
    list_filter = ('usuario__tipo',)

@admin.register(MicroempresaSatelite)
class MicroempresaSateliteAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'rut_empresa', 'usuario')
    search_fields = ('nombre_empresa', 'rut_empresa')
    list_filter = ('usuario__tipo',)

@admin.register(ProductoTerminado)
class ProductoTerminadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'precio', 'stock', 'categoria')
    search_fields = ('nombre', 'empresa__nombre')
    list_filter = ('categoria', 'empresa')

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'cantidad', 'unidad_medida', 'precio_unitario')
    search_fields = ('nombre', 'empresa__nombre')
    list_filter = ('empresa', 'unidad_medida')

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'descripcion', 'precio_minimo', 'precio_maximo')
    search_fields = ('nombre', 'empresa__nombre_empresa')
    list_filter = ('empresa',)
