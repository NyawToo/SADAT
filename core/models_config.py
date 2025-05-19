from django.db import models

class ConfiguracionSistema(models.Model):
    iva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25.00,
        help_text='Porcentaje de IVA aplicado a las ventas'
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='actualizaciones_config'
    )

    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'

    def __str__(self):
        return f'Configuración del Sistema (IVA: {self.iva}%)'