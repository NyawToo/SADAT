from django.db import models
from .models import MicroempresaIntegral

class CategoriaMateriaPrima(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    empresa = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE, related_name='categorias_materia_prima', null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Categoría de Materia Prima'
        verbose_name_plural = 'Categorías de Materia Prima'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} - {self.empresa.nombre}'

class MateriaPrima(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(CategoriaMateriaPrima, on_delete=models.CASCADE, related_name='materias_primas', null=True, blank=True)
    cantidad = models.IntegerField(default=0)
    unidad_medida = models.CharField(max_length=50, null=True)
    precio_unitario = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    empresa = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE, related_name='materias_primas', null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Materia Prima'
        verbose_name_plural = 'Materias Primas'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return f'{self.nombre} - {self.categoria.nombre}'

class MovimientoMateriaPrima(models.Model):
    TIPO_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida')
    ]

    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE, related_name='movimientos', null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO, null=True)
    cantidad = models.IntegerField(null=True)
    fecha = models.DateTimeField(auto_now_add=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Movimiento de Materia Prima'
        verbose_name_plural = 'Movimientos de Materia Prima'
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        if self.tipo == 'entrada':
            self.materia_prima.cantidad += self.cantidad
        else:
            self.materia_prima.cantidad -= self.cantidad
        self.materia_prima.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.tipo} - {self.materia_prima.nombre} - {self.cantidad}'