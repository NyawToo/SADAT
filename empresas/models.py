from django.db import models
from core.models import Usuario

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'

    def __str__(self):
        return self.nombre

class MicroempresaIntegral(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre_empresa = models.CharField(max_length=100)
    descripcion = models.TextField()
    rut_empresa = models.CharField(max_length=20, unique=True)
    imagen = models.ImageField(upload_to='logos_integral/', null=True, blank=True)

# La clase MateriaPrima se ha movido a models_materia_prima.py

class ProductoTerminado(models.Model):
    empresa = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, related_name='productos', null=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    
    def get_upload_path(instance, filename):
        return f'integrales/{instance.empresa.nombre_empresa}/{filename}'
    
    imagen = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Producto Terminado'
        verbose_name_plural = 'Productos Terminados'

class ComentarioProducto(models.Model):
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha']

class CalificacionProducto(models.Model):
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE, related_name='calificaciones')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    puntuacion = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = ['producto', 'usuario']

class MicroempresaSatelite(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre_empresa = models.CharField(max_length=100)
    descripcion = models.TextField()
    rut_empresa = models.CharField(max_length=20, unique=True)
    imagen = models.ImageField(upload_to='logos_satelite/', null=True, blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    tipo = models.CharField(max_length=20, default='satelite')

    def get_tipo_display(self):
        return 'Satélite'

class Maquina(models.Model):
    empresa = models.ForeignKey(MicroempresaSatelite, on_delete=models.CASCADE, related_name='maquinaria')
    nombre = models.CharField(max_length=100, default='Nueva Máquina')
    tipo = models.CharField(max_length=50, default='Industrial')
    marca = models.CharField(max_length=50, default='Sin Especificar')
    modelo = models.CharField(max_length=50, default='Sin Especificar')
    cantidad = models.PositiveIntegerField(default=1)
    descripcion = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('activa', 'Activa'),
        ('mantenimiento', 'En Mantenimiento'),
        ('inactiva', 'Inactiva')
    ], default='activa')
    
    def get_upload_path(instance, filename):
        return f'maquinaria/{instance.empresa.nombre_empresa}/{filename}'
    
    imagen = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Máquina'
        verbose_name_plural = 'Máquinas'
        
    def __str__(self):
        return f'{self.nombre} - {self.empresa.nombre_empresa}'

class Servicio(models.Model):
    empresa = models.ForeignKey(MicroempresaSatelite, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_maximo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return f'{self.nombre} - {self.empresa.nombre_empresa}'