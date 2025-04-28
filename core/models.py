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
