from django.db import models
from core.models import Usuario
from pedidos.models import Pedido, PedidoPersonalizado, SolicitudConfeccion

class Transaccion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completada', 'Completada'),
        ('fallida', 'Fallida'),
        ('reembolsada', 'Reembolsada')
    ]
    
    TIPOS = [
        ('pedido_estandar', 'Pedido Estándar'),
        ('pedido_personalizado', 'Pedido Personalizado'),
        ('solicitud_confeccion', 'Solicitud de Confección')
    ]
    
    METODOS_PAGO = [
        ('card', 'Tarjeta de Crédito/Débito'),
        ('transfer', 'Transferencia Bancaria'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    tipo_transaccion = models.CharField(max_length=30, choices=TIPOS)
    
    # Referencias opcionales a diferentes tipos de pedidos
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pedido_personalizado = models.OneToOneField(
        PedidoPersonalizado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    solicitud_confeccion = models.OneToOneField(
        SolicitudConfeccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Campos para la integración con Stripe
    stripe_payment_intent_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    stripe_payment_method_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    metodo_pago = models.CharField(max_length=50, choices=METODOS_PAGO, null=True)
    detalles_pago = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Transacción #{self.id} - {self.usuario.username} - ${self.monto}'
