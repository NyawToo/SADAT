from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo', 'is_active', 'is_staff')
    list_filter = ('tipo', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('email', 'tipo', 'telefono', 'direccion')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'tipo', 'password1', 'password2'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        from django.db import transaction
        from empresas.models import MicroempresaIntegral, MicroempresaSatelite
        from pedidos.models import Pedido, PedidoPersonalizado, Carrito, ItemCarrito, DetallePedido
        from pagos.models import Transaccion
        
        with transaction.atomic():
            # Guardar el tipo original antes de los cambios
            original_tipo = None
            if change:
                original = Usuario.objects.get(pk=obj.pk)
                original_tipo = original.tipo
            
            # Si cambia a superusuario
            if 'is_superuser' in form.changed_data or ('tipo' in form.changed_data and obj.tipo == 'superusuario'):
                # Eliminar relaciones existentes en orden correcto
                # Primero eliminar los items del carrito
                carritos = Carrito.objects.filter(usuario=obj)
                ItemCarrito.objects.filter(carrito__in=carritos).delete()
                carritos.delete()
                
                # Eliminar detalles de pedidos antes que los pedidos
                pedidos = Pedido.objects.filter(cliente=obj)
                DetallePedido.objects.filter(pedido__in=pedidos).delete()
                pedidos.delete()
                
                # Eliminar otros registros relacionados
                PedidoPersonalizado.objects.filter(cliente=obj).delete()
                Transaccion.objects.filter(usuario=obj).delete()
                
                try:
                    if hasattr(obj, 'microempresaintegral'):
                        obj.microempresaintegral.delete()
                except MicroempresaIntegral.DoesNotExist:
                    pass
                    
                try:
                    if hasattr(obj, 'microempresasatelite'):
                        obj.microempresasatelite.delete()
                except MicroempresaSatelite.DoesNotExist:
                    pass
                
                obj.tipo = 'superusuario'
                obj.is_superuser = True
                obj.is_staff = True
            
            # Si cambia de superusuario a otro tipo
            elif original_tipo == 'superusuario' and 'tipo' in form.changed_data:
                obj.is_superuser = False
                if obj.tipo not in ['integral', 'satelite']:
                    obj.is_staff = False
            
            # Si cambia a empresa
            elif 'tipo' in form.changed_data and obj.tipo in ['integral', 'satelite']:
                empresa_exists = False
                if obj.tipo == 'integral':
                    empresa_exists = MicroempresaIntegral.objects.filter(usuario=obj).exists()
                elif obj.tipo == 'satelite':
                    empresa_exists = MicroempresaSatelite.objects.filter(usuario=obj).exists()
                
                if not empresa_exists:
                    obj.tipo = 'cliente'
                    obj.is_staff = False
                else:
                    obj.is_staff = True
            
            # Si cambia a cliente
            elif 'tipo' in form.changed_data and obj.tipo == 'cliente':
                obj.is_superuser = False
                obj.is_staff = False
            
            super().save_model(request, obj, form, change)

admin.site.register(Usuario, CustomUserAdmin)
