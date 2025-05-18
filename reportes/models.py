from django.db import models
from core.models import Usuario
from empresas.models import MicroempresaIntegral, MicroempresaSatelite
from pedidos.models import Pedido, PedidoPersonalizado, SolicitudConfeccion

class Reporte(models.Model):
    TIPOS = [
        ('ventas', 'Reporte de Ventas'),
        ('produccion', 'Reporte de Producción'),
        ('inventario', 'Reporte de Inventario'),
        ('financiero', 'Reporte Financiero')
    ]
    
    empresa_integral = models.ForeignKey(
        MicroempresaIntegral,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    empresa_satelite = models.ForeignKey(
        MicroempresaSatelite,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    tipo_reporte = models.CharField(max_length=20, choices=TIPOS)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    datos = models.JSONField(default=dict)
    archivo_pdf = models.FileField(
        upload_to='reportes/',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        empresa = self.empresa_integral or self.empresa_satelite
        return f'{self.get_tipo_reporte_display()} - {empresa} ({self.fecha_inicio} a {self.fecha_fin})'

class Estadistica(models.Model):
    PERIODOS = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('anual', 'Anual')
    ]
    
    empresa_integral = models.ForeignKey(
        MicroempresaIntegral,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    empresa_satelite = models.ForeignKey(
        MicroempresaSatelite,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    periodo = models.CharField(max_length=20, choices=PERIODOS)
    fecha = models.DateField()
    ventas_totales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pedidos_completados = models.PositiveIntegerField(default=0)
    pedidos_pendientes = models.PositiveIntegerField(default=0)
    produccion_total = models.PositiveIntegerField(default=0)
    ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Estadística'
        verbose_name_plural = 'Estadísticas'
        ordering = ['-fecha']
        unique_together = [['empresa_integral', 'empresa_satelite', 'periodo', 'fecha']]
    
    def __str__(self):
        empresa = self.empresa_integral or self.empresa_satelite
        return f'Estadísticas {self.get_periodo_display()} - {empresa} ({self.fecha})'

class Queja(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelta', 'Resuelta')
    ]
    
    TIPOS = [
        ('producto', 'Producto'),
        ('servicio', 'Servicio'),
        ('pago', 'Pago'),
        ('otro', 'Otro')
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    respuesta = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Queja'
        verbose_name_plural = 'Quejas'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Queja de {self.usuario.username} - {self.get_tipo_display()} ({self.get_estado_display()})'
