from django.contrib import admin
from .models import Transaccion

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'monto', 'estado', 'tipo_transaccion', 'fecha_creacion')
    list_filter = ('estado', 'tipo_transaccion', 'fecha_creacion')
    search_fields = ('usuario__username', 'pedido__id')
    date_hierarchy = 'fecha_creacion'
    
    readonly_fields = ('stripe_payment_intent_id', 'detalles_pago')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('usuario', 'monto', 'estado', 'tipo_transaccion')
        }),
        ('Detalles del Pedido', {
            'fields': ('pedido', 'metodo_pago')
        }),
        ('Información de Stripe', {
            'fields': ('stripe_payment_intent_id', 'detalles_pago')
        })
    )
