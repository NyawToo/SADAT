from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    ROLES = [
        ('integral', 'Microempresa Integral'),
        ('satelite', 'Microempresa Satélite'),
        ('cliente', 'Cliente'),
        ('superusuario', 'Super Usuario'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=ROLES,
        default='cliente'
    )
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f'{self.username} ({self.get_tipo_display()})'
    
    def save(self, *args, **kwargs):
        # Validar y sincronizar tipo de usuario con permisos
        if self.is_superuser:
            self.tipo = 'superusuario'
            self.is_staff = True
        elif self.tipo == 'superusuario' and not self.is_superuser:
            self.tipo = 'cliente'
            self.is_staff = False
        
        # Asegurar que usuarios empresariales tengan is_staff
        if self.tipo in ['integral', 'satelite']:
            self.is_staff = True
        
        # Validar existencia de empresa antes de guardar
        if not self._state.adding:  # Si no es una nueva instancia
            from empresas.models import MicroempresaIntegral, MicroempresaSatelite
            
            if self.tipo == 'integral':
                try:
                    MicroempresaIntegral.objects.get(usuario=self)
                except MicroempresaIntegral.DoesNotExist:
                    self.tipo = 'cliente'
            
            elif self.tipo == 'satelite':
                try:
                    MicroempresaSatelite.objects.get(usuario=self)
                except MicroempresaSatelite.DoesNotExist:
                    self.tipo = 'cliente'
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Eliminar registros relacionados en orden específico para evitar errores de FK
        from empresas.models import MicroempresaIntegral, MicroempresaSatelite
        from pedidos.models import Pedido, PedidoPersonalizado, Carrito
        from pagos.models import Transaccion
        
        # Eliminar carrito y sus items
        Carrito.objects.filter(usuario=self).delete()
        
        # Eliminar transacciones
        Transaccion.objects.filter(usuario=self).delete()
        
        # Eliminar pedidos y pedidos personalizados
        Pedido.objects.filter(cliente=self).delete()
        PedidoPersonalizado.objects.filter(cliente=self).delete()
        
        # Eliminar microempresas asociadas
        try:
            if hasattr(self, 'microempresaintegral'):
                self.microempresaintegral.delete()
        except MicroempresaIntegral.DoesNotExist:
            pass
            
        try:
            if hasattr(self, 'microempresasatelite'):
                self.microempresasatelite.delete()
        except MicroempresaSatelite.DoesNotExist:
            pass
        
        # Finalmente eliminar el usuario
        super().delete(*args, **kwargs)
