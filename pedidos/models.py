from django.db import models
from core.models import Usuario
from empresas.models import MicroempresaIntegral, MicroempresaSatelite, ProductoTerminado

class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Carrito de {self.usuario.username}'

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

    class Meta:
        unique_together = ('carrito', 'producto')

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_produccion', 'En Producción'),
        ('terminado', 'Terminado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado')
    ]
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos', null=True, blank=True)
    empresa = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE, related_name='pedidos')
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.username}'

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

class PedidoPersonalizado(models.Model):
    ESTADOS = [
        ('solicitado', 'Solicitado'),
        ('cotizado', 'Cotizado'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado')
    ]
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    empresa = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE)
    descripcion = models.TextField()
    referencia_imagen = models.ImageField(upload_to='pedidos_personalizados/', null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='solicitado')
    cotizacion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_cotizacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido Personalizado'
        verbose_name_plural = 'Pedidos Personalizados'

class SolicitudConfeccion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('cotizada', 'Cotizada'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada')
    ]
    
    empresa_integral = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE, null=True, blank=True)
    empresa_satelite = models.ForeignKey(MicroempresaSatelite, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    descripcion = models.TextField()
    cantidad_prendas = models.PositiveIntegerField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_entrega_requerida = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    cotizacion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    material_cliente = models.BooleanField(default=False)
    descripcion_material = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Solicitud de Confección'
        verbose_name_plural = 'Solicitudes de Confección'

    def __str__(self):
        return f"Solicitud #{self.id} - {self.cliente.username}"