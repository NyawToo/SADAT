from django.contrib import admin
from .models import Pedido, DetallePedido, Carrito, ItemCarrito, SolicitudConfeccion

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'empresa', 'fecha_pedido', 'estado', 'total')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('cliente__username', 'empresa__nombre_empresa')
    date_hierarchy = 'fecha_pedido'

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')
    search_fields = ('pedido__id', 'producto__nombre')
    list_filter = ('pedido__estado',)

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_creacion')
    search_fields = ('usuario__username',)

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad')
    search_fields = ('carrito__usuario__username', 'producto__nombre')

@admin.register(SolicitudConfeccion)
class SolicitudConfeccionAdmin(admin.ModelAdmin):
    list_display = ('empresa_integral', 'empresa_satelite', 'fecha_solicitud', 'estado')
    list_filter = ('estado', 'empresa_integral', 'empresa_satelite')
    search_fields = ('empresa_integral__nombre', 'empresa_satelite__nombre')
    date_hierarchy = 'fecha_solicitud'
