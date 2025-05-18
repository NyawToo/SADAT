from django.db import models
from core.models import Usuario
from pedidos.models import Pedido, PedidoPersonalizado, SolicitudConfeccion
from empresas.models import MicroempresaIntegral, MicroempresaSatelite

class Notificacion(models.Model):
    TIPOS = [
        ('pedido_actualizado', 'Pedido Actualizado'),
        ('pago_recibido', 'Pago Recibido'),
        ('solicitud_nueva', 'Nueva Solicitud'),
        ('alerta_inventario', 'Alerta de Inventario'),
        ('recordatorio', 'Recordatorio'),
        ('sistema', 'Sistema')
    ]
    
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta')
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    # Referencias opcionales a diferentes entidades
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pedido_personalizado = models.ForeignKey(
        PedidoPersonalizado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    solicitud_confeccion = models.ForeignKey(
        SolicitudConfeccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.titulo}'

class ConfiguracionNotificaciones(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    notificar_pedidos = models.BooleanField(default=True)
    notificar_pagos = models.BooleanField(default=True)
    notificar_solicitudes = models.BooleanField(default=True)
    notificar_inventario = models.BooleanField(default=True)
    notificar_recordatorios = models.BooleanField(default=True)
    notificar_sistema = models.BooleanField(default=True)
    
    # Preferencias de notificación por email
    email_pedidos = models.BooleanField(default=True)
    email_pagos = models.BooleanField(default=True)
    email_solicitudes = models.BooleanField(default=True)
    email_inventario = models.BooleanField(default=False)
    email_recordatorios = models.BooleanField(default=False)
    email_sistema = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Configuración de Notificaciones'
        verbose_name_plural = 'Configuraciones de Notificaciones'
    
    def __str__(self):
        return f'Configuración de notificaciones - {self.usuario}'
