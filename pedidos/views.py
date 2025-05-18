from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Pedido, PedidoPersonalizado, SolicitudConfeccion, Carrito, ItemCarrito
from empresas.models import MicroempresaIntegral, MicroempresaSatelite, ProductoTerminado, CategoriaProducto, Servicio
from notificaciones.models import Notificacion
from pagos.models import Transaccion
from core.decorators import role_required
from django.utils import timezone
from decimal import Decimal
import json
import datetime

@login_required
@role_required(['superusuario'])
def categorias(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        
        if nombre:
            CategoriaProducto.objects.create(
                nombre=nombre
            )
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('categorias')
        else:
            messages.error(request, 'El nombre de la categoría es requerido')
    
    categorias = CategoriaProducto.objects.all().order_by('nombre')
    return render(request, 'pedidos/categorias.html', {'categorias': categorias})

@login_required
@role_required(['superusuario'])
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        
        if nombre:
            categoria.nombre = nombre
            categoria.descripcion = descripcion or ''
            categoria.save()
            messages.success(request, 'Categoría actualizada exitosamente')
        else:
            messages.error(request, 'El nombre de la categoría es requerido')
    
    return redirect('categorias')

@login_required
@role_required(['superusuario'])
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
    
    try:
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente')
    except Exception as e:
        messages.error(request, 'No se pudo eliminar la categoría. Verifica que no tenga productos asociados.')
    
    return redirect('categorias')

@login_required
def carrito(request):
    carrito_obj, created = Carrito.objects.get_or_create(usuario=request.user)
    items_carrito = ItemCarrito.objects.filter(carrito=carrito_obj).select_related('producto')
    
    # Calcular subtotal por producto y totales
    for item in items_carrito:
        item.subtotal = float(item.producto.precio) * item.cantidad
    
    subtotal = sum(item.subtotal for item in items_carrito)
    iva = round(subtotal * 0.19, 2)
    total = round(subtotal + iva, 2)
    
    context = {
        'items_carrito': items_carrito,
        'subtotal': round(subtotal, 2),
        'iva': iva,
        'total': total
    }
    return render(request, 'pedidos/carrito.html', context)

@login_required
def gestionar_pedidos(request):
    user = request.user
    if user.tipo == 'integral':
        empresa = MicroempresaIntegral.objects.get(usuario=user)
        pedidos = Pedido.objects.filter(empresa=empresa)
        
        # Aplicar filtros si existen
        estado = request.GET.get('estado')
        fecha = request.GET.get('fecha')
        
        if estado:
            pedidos = pedidos.filter(estado=estado)
        if fecha:
            pedidos = pedidos.filter(fecha_pedido__date=fecha)
            
        # Obtener notificaciones relacionadas con pedidos
        notificaciones = Notificacion.objects.filter(
            usuario=user,
            tipo__in=['pedido_nuevo', 'pedido_actualizado', 'sistema'],
            leida=False
        ).order_by('-fecha_creacion')
        
        return render(request, 'pedidos/gestionar_pedidos.html', {
            'pedidos': pedidos.order_by('-fecha_pedido'),
            'notificaciones': notificaciones
        })
    else:
        messages.error(request, 'No tienes permiso para ver esta página')
        return redirect('dashboard')

@login_required
def gestionar_pedidos_personalizados(request):
    user = request.user
    if user.tipo == 'integral':
        empresa = MicroempresaIntegral.objects.get(usuario=user)
        pedidos_personalizados = PedidoPersonalizado.objects.filter(empresa=empresa).order_by('-fecha_solicitud')
        
        # Aplicar filtros si existen
        estado = request.GET.get('estado')
        fecha = request.GET.get('fecha')
        
        if estado:
            pedidos_personalizados = pedidos_personalizados.filter(estado=estado)
        if fecha:
            pedidos_personalizados = pedidos_personalizados.filter(fecha_solicitud__date=fecha)
        
        return render(request, 'pedidos/gestionar_pedidos_personalizados.html', {
            'pedidos': pedidos_personalizados,
            'ESTADOS': PedidoPersonalizado.ESTADOS
        })
    else:
        messages.error(request, 'No tienes permiso para ver esta página')
        return redirect('dashboard')

@login_required
def actualizar_pedido_personalizado(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(PedidoPersonalizado, id=pedido_id, empresa__usuario=request.user)
        estado = request.POST.get('estado')
        cotizacion = request.POST.get('cotizacion')
        
        if estado in dict(PedidoPersonalizado.ESTADOS).keys():
            pedido.estado = estado
            if cotizacion:
                pedido.cotizacion = cotizacion
            pedido.save()
            
            # Crear notificación para el cliente
            Notificacion.objects.create(
                usuario=pedido.cliente,
                tipo='pedido_personalizado',
                titulo='Actualización de pedido personalizado',
                mensaje=f'Tu pedido personalizado #{pedido.id} ha sido actualizado a estado: {pedido.get_estado_display()}',
                prioridad='alta'
            )
            
            messages.success(request, 'Pedido actualizado exitosamente')
        else:
            messages.error(request, 'Estado no válido')
    
    return redirect('gestionar_pedidos_personalizados')

@login_required
def gestionar_solicitudes_confeccion(request):
    user = request.user
    if user.tipo == 'satelite':
        empresa = MicroempresaSatelite.objects.get(usuario=user)
        solicitudes = SolicitudConfeccion.objects.filter(empresa_satelite=empresa).order_by('-fecha_solicitud')
        
        # Aplicar filtros si existen
        estado = request.GET.get('estado')
        fecha = request.GET.get('fecha')
        
        if estado:
            solicitudes = solicitudes.filter(estado=estado)
        if fecha:
            try:
                fecha_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                solicitudes = solicitudes.filter(fecha_entrega_requerida=fecha_obj)
            except (ValueError, TypeError):
                messages.error(request, 'Formato de fecha inválido')
                return redirect('gestionar_solicitudes_confeccion')
            
        return render(request, 'pedidos/gestionar_solicitudes_confeccion.html', {
            'solicitudes': solicitudes,
            'estado_filtro': estado,
            'fecha_filtro': fecha
        })
    else:
        messages.error(request, 'No tiene permisos para acceder a esta página')
        return redirect('home')

@login_required
def responder_cotizacion_personalizada(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(PedidoPersonalizado, id=pedido_id, cliente=request.user)
        accion = request.POST.get('accion')
        
        if accion == 'aceptar':
            pedido.estado = 'aceptado'
            messages.success(request, 'Has aceptado la cotización del pedido personalizado.')
            
            # Crear notificación para la empresa
            Notificacion.objects.create(
                usuario=pedido.empresa.usuario,
                tipo='pedido_personalizado',
                titulo='Cotización aceptada',
                mensaje=f'El cliente ha aceptado la cotización del pedido personalizado #{pedido.id}',
                prioridad='alta'
            )
        elif accion == 'rechazar':
            pedido.estado = 'rechazado'
            messages.info(request, 'Has rechazado la cotización del pedido personalizado.')
            
            # Crear notificación para la empresa
            Notificacion.objects.create(
                usuario=pedido.empresa.usuario,
                tipo='pedido_personalizado',
                titulo='Cotización rechazada',
                mensaje=f'El cliente ha rechazado la cotización del pedido personalizado #{pedido.id}',
                prioridad='alta'
            )
        
        pedido.save()
        return redirect('mis_pedidos')
    
    return redirect('mis_pedidos')

@login_required
def lista_productos(request):
    return render(request, 'pedidos/lista_productos.html')

@login_required
@role_required(['cliente'])
def detalle_producto(request, producto_id):
    producto = get_object_or_404(ProductoTerminado, id=producto_id)
    return render(request, 'pedidos/producto.html', {'producto': producto})

@login_required
@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(ProductoTerminado, id=producto_id)
    
    # Añadir manejo de errores para la conversión de cantidad
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'La cantidad proporcionada no es válida.'})
    
    if cantidad <= 0:
        return JsonResponse({'success': False, 'error': 'La cantidad debe ser mayor a 0'})
    
    if cantidad > producto.stock:
        return JsonResponse({'success': False, 'error': 'No hay suficiente stock disponible'})
    
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    item_carrito, item_created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    
    if not item_created:
        item_carrito.cantidad += cantidad
        item_carrito.save()
    
    producto.stock -= cantidad
    producto.save()
    
    # Crear notificación para la empresa integral
    Notificacion.objects.create(
        usuario=producto.empresa.usuario,
        tipo='sistema',
        titulo='Nuevo producto en carrito',
        mensaje=f'El cliente {request.user.username} ha agregado {cantidad} unidad(es) de {producto.nombre} a su carrito.',
        prioridad='media'
    )
    
    return JsonResponse({
        'success': True,
        'nuevo_stock': producto.stock
    })

@login_required
def productos_integral(request):
    try:
        empresa = request.user.microempresaintegral
    except MicroempresaIntegral.DoesNotExist:
        raise PermissionDenied("Solo las empresas integrales pueden acceder a esta página")
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        imagen = request.FILES.get('imagen')
        
        ProductoTerminado.objects.create(
            empresa=empresa,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen
        )
        return redirect('productos_integral')
    
    productos = ProductoTerminado.objects.filter(empresa=empresa)
    return render(request, 'pedidos/productos_integral.html', {
        'productos': productos
    })

@login_required
def editar_producto(request, pk):
    try:
        empresa = request.user.microempresaintegral
    except MicroempresaIntegral.DoesNotExist:
        raise PermissionDenied
    
    producto = get_object_or_404(ProductoTerminado, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        
        producto.save()
        return redirect('productos_integral')
    
    return render(request, 'pedidos/productos_integral.html', {
        'producto': producto,
        'editing': True
    })

@login_required
def eliminar_producto(request, pk):
    if request.method == 'POST':
        try:
            empresa = request.user.microempresaintegral
            producto = get_object_or_404(ProductoTerminado, pk=pk, empresa=empresa)
            producto.delete()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})

@login_required
def mis_pedidos(request):
    try:
        # Obtener todos los pedidos estándar del usuario
        pedidos_estandar = Pedido.objects.filter(cliente=request.user).select_related('empresa', 'producto').order_by('-fecha_pedido')
        
        # Obtener pedidos personalizados
        pedidos_personalizados = PedidoPersonalizado.objects.filter(
            cliente=request.user
        ).select_related('empresa').order_by('-fecha_solicitud')
        
        # Obtener solicitudes de confección
        solicitudes_confeccion = SolicitudConfeccion.objects.filter(
            cliente=request.user
        ).select_related('empresa_satelite').order_by('-fecha_solicitud')
        
        # Obtener carrito actual si existe
        carrito = Carrito.objects.filter(usuario=request.user).first()
        if carrito:
            items_carrito = ItemCarrito.objects.filter(carrito=carrito).select_related('producto', 'producto__empresa')
            # Convertir items del carrito a lista de pedidos temporales
            pedidos_temp = []
            for item in items_carrito:
                pedido_temp = Pedido(
                    cliente=request.user,
                    empresa=item.producto.empresa,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    fecha_pedido=carrito.fecha_creacion,
                    fecha_entrega=timezone.now().date(),
                    estado='pendiente',
                    total=Decimal(str(item.producto.precio * item.cantidad))
                )
                pedidos_temp.append(pedido_temp)
            
            # Combinar pedidos existentes con temporales
            pedidos_estandar = list(pedidos_estandar) + pedidos_temp
        
        return render(request, 'pedidos/mis_pedidos.html', {
            'pedidos_estandar': pedidos_estandar,
            'pedidos_personalizados': pedidos_personalizados,
            'solicitudes_confeccion': solicitudes_confeccion
        })
    except Exception as e:
        messages.error(request, f'Error al cargar los pedidos: {str(e)}')
        return redirect('home')

@login_required
def solicitar_confeccion(request, servicio_id=None):
    if request.user.tipo != 'cliente':
        messages.error(request, 'Solo los clientes pueden solicitar confección')
        return redirect('home')
    
    servicio = None
    empresa_satelite = None
    if servicio_id:
        servicio = get_object_or_404(Servicio, id=servicio_id)
        empresa_satelite = servicio.empresa
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        fecha_entrega = request.POST.get('fecha_entrega')
        cantidad = request.POST.get('cantidad')
        precio = request.POST.get('precio')
        material_cliente = request.POST.get('material_cliente') == 'si'
        descripcion_material = request.POST.get('descripcion_material')

        # Validar campos requeridos
        if not all([descripcion, fecha_entrega, cantidad, precio]):
            messages.error(request, 'Por favor complete todos los campos requeridos.')
            return render(request, 'pedidos/solicitar_confeccion.html', {
                'servicio': servicio,
                'empresa_satelite': empresa_satelite,
                'form_data': request.POST,
            })

        # Validar cantidad y precio
        try:
            cantidad = int(cantidad)
            precio = float(precio)
            if cantidad <= 0 or precio <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'La cantidad y el precio deben ser valores numéricos válidos y positivos.')
            return render(request, 'pedidos/solicitar_confeccion.html', {
                'servicio': servicio,
                'empresa_satelite': empresa_satelite,
                'form_data': request.POST,
            })

        # Validar rango de precios
        if servicio and (precio < float(servicio.precio_minimo) or precio > float(servicio.precio_maximo)):
            messages.error(request, f'El precio debe estar entre ${servicio.precio_minimo} y ${servicio.precio_maximo}')
            return render(request, 'pedidos/solicitar_confeccion.html', {
                'servicio': servicio,
                'empresa_satelite': empresa_satelite,
                'form_data': request.POST,
            })

        # Validar fecha de entrega
        try:
            fecha_entrega_dt = datetime.datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
            if fecha_entrega_dt < timezone.now().date():
                messages.error(request, 'La fecha de entrega debe ser una fecha futura.')
                return render(request, 'pedidos/solicitar_confeccion.html', {
                    'servicio': servicio,
                    'empresa_satelite': empresa_satelite,
                    'form_data': request.POST,
                })
        except ValueError:
            messages.error(request, 'Formato de fecha inválido.')
            return render(request, 'pedidos/solicitar_confeccion.html', {
                'servicio': servicio,
                'empresa_satelite': empresa_satelite,
                'form_data': request.POST,
            })

        # Validar empresa satélite
        if not empresa_satelite:
            messages.error(request, 'Empresa satélite no encontrada')
            return render(request, 'pedidos/solicitar_confeccion.html', {
                'servicio': servicio,
                'empresa_satelite': empresa_satelite,
                'form_data': request.POST,
            })

        try:
            # Crear la solicitud
            solicitud = SolicitudConfeccion.objects.create(
                empresa_integral=None,
                empresa_satelite=empresa_satelite,
                cliente=request.user,
                descripcion=descripcion,
                cantidad_prendas=cantidad,
                fecha_entrega_requerida=fecha_entrega,
                cotizacion=precio,
                estado='pendiente',
                material_cliente=material_cliente,
                descripcion_material=descripcion_material if material_cliente else None
            )

            # Crear notificación
            Notificacion.objects.create(
                usuario=empresa_satelite.usuario,
                tipo='solicitud_confeccion',
                titulo='Nueva solicitud de confección',
                mensaje=f'Has recibido una nueva solicitud de confección del cliente {request.user.username} (Solicitud #{solicitud.id})',
                prioridad='alta'
            )

            messages.success(request, 'Solicitud de confección enviada exitosamente')
            return redirect('catalogo_satelites')

        except Exception as e:
            messages.error(request, f'Error al crear la solicitud: {str(e)}')
            return render(request, 'pedidos/solicitar_confeccion.html', {
                'servicio': servicio,
                'empresa_satelite': empresa_satelite,
                'form_data': request.POST,
            })

    return render(request, 'pedidos/solicitar_confeccion.html', {
        'servicio': servicio,
        'empresa_satelite': empresa_satelite,
    })

@login_required
def solicitar_pedido_personalizado(request, empresa_id):
    try:
        empresa = MicroempresaIntegral.objects.get(id=empresa_id)
    except MicroempresaIntegral.DoesNotExist:
        messages.error(request, 'Empresa no encontrada')
        return redirect('catalogo_integrales')

    if request.method == 'POST':
        try:
            descripcion = request.POST.get('descripcion')
            cantidad = request.POST.get('cantidad')
            fecha_entrega_estimada = request.POST.get('fecha_entrega_estimada')
            referencia_imagen = request.FILES.get('referencia_imagen')
            
            # Validar campos requeridos
            if not all([descripcion, cantidad, fecha_entrega_estimada]):
                messages.error(request, 'Por favor complete todos los campos requeridos')
                return render(request, 'pedidos/solicitar_pedido_personalizado.html', {
                    'empresa': empresa,
                    'form_data': request.POST
                })
            
            # Validar cantidad
            try:
                cantidad = int(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, 'La cantidad debe ser un número entero positivo')
                return render(request, 'pedidos/solicitar_pedido_personalizado.html', {
                    'empresa': empresa,
                    'form_data': request.POST
                })
            
            # Validar fecha
            try:
                fecha_entrega = datetime.datetime.strptime(fecha_entrega_estimada, '%Y-%m-%d').date()
                if fecha_entrega < timezone.now().date():
                    messages.error(request, 'La fecha de entrega debe ser una fecha futura')
                    return render(request, 'pedidos/solicitar_pedido_personalizado.html', {
                        'empresa': empresa,
                        'form_data': request.POST
                    })
            except ValueError:
                messages.error(request, 'Formato de fecha inválido')
                return render(request, 'pedidos/solicitar_pedido_personalizado.html', {
                    'empresa': empresa,
                    'form_data': request.POST
                })
            
            # Crear pedido personalizado
            pedido = PedidoPersonalizado.objects.create(
                cliente=request.user,
                empresa=empresa,
                descripcion=descripcion,
                cantidad=cantidad,
                fecha_entrega_estimada=fecha_entrega,
                referencia_imagen=referencia_imagen,
                estado='pendiente'
            )
            
            # Crear notificación para la empresa
            Notificacion.objects.create(
                usuario=empresa.usuario,
                tipo='pedido_personalizado',
                titulo='Nuevo pedido personalizado',
                mensaje=f'Has recibido un nuevo pedido personalizado del cliente {request.user.username}',
                prioridad='alta'
            )
            
            messages.success(request, 'Pedido personalizado enviado exitosamente')
            return redirect('mis_pedidos')
            
        except Exception as e:
            messages.error(request, 'Ocurrió un error al procesar tu pedido. Por favor intenta nuevamente.')
            return render(request, 'pedidos/solicitar_pedido_personalizado.html', {'empresa': empresa})
    
    return render(request, 'pedidos/solicitar_pedido_personalizado.html', {'empresa': empresa})

@login_required
def dashboard(request):
    context = {}
    user = request.user
    
    if user.tipo == 'integral':
        empresa = MicroempresaIntegral.objects.get(usuario=user)
        pedidos = Pedido.objects.filter(empresa=empresa)
        pedidos_personalizados = PedidoPersonalizado.objects.filter(empresa=empresa)
        solicitudes = SolicitudConfeccion.objects.filter(empresa_integral=empresa)
        
        context.update({
            'pedidos_pendientes': pedidos.filter(estado='pendiente').count(),
            'pedidos_proceso': pedidos.filter(estado='en_proceso').count(),
            'pedidos_completados': pedidos.filter(estado='completado').count(),
            'pedidos_personalizados': pedidos_personalizados.count(),
            'solicitudes_confeccion': solicitudes.count(),
            'ingresos_totales': Transaccion.objects.filter(
                Q(pedido__empresa=empresa) |
                Q(pedido_personalizado__empresa=empresa),
                estado='completada'
            ).aggregate(total=Sum('monto'))['total'] or 0
        })
    
    elif user.tipo == 'satelite':
        empresa = MicroempresaSatelite.objects.get(usuario=user)
        solicitudes = SolicitudConfeccion.objects.filter(empresa_satelite=empresa)
        
        context.update({
            'solicitudes_pendientes': solicitudes.filter(estado='pendiente').count(),
            'solicitudes_proceso': solicitudes.filter(estado='en_proceso').count(),
            'solicitudes_completadas': solicitudes.filter(estado='completada').count(),
            'ingresos_totales': Transaccion.objects.filter(
                solicitud_confeccion__empresa_satelite=empresa,
                estado='completada'
            ).aggregate(total=Sum('monto'))['total'] or 0
        })
    
    elif user.tipo == 'cliente':
        pedidos = Pedido.objects.filter(cliente=user)
        pedidos_personalizados = PedidoPersonalizado.objects.filter(cliente=user)
        
        context.update({
            'pedidos_activos': pedidos.exclude(estado='completado').count(),
            'pedidos_completados': pedidos.filter(estado='completado').count(),
            'pedidos_personalizados_activos': pedidos_personalizados.exclude(
                estado='completado'
            ).count(),
            'total_gastado': Transaccion.objects.filter(
                usuario=user,
                estado='completada'
            ).aggregate(total=Sum('monto'))['total'] or 0
        })
    
    context['notificaciones'] = Notificacion.objects.filter(
        usuario=user,
        leida=False
    ).order_by('-fecha_creacion')[:5]
    
    return render(request, 'pedidos/dashboard.html', context)

@login_required
def lista_pedidos(request):
    user = request.user
    
    if user.tipo == 'integral':
        empresa = MicroempresaIntegral.objects.get(usuario=user)
        pedidos = Pedido.objects.filter(empresa=empresa)
    elif user.tipo == 'cliente':
        pedidos = Pedido.objects.filter(cliente=user)
    else:
        messages.error(request, 'No tienes permiso para ver esta página')
        return redirect('dashboard')
    
    context = {
        'pedidos': pedidos.order_by('-fecha_pedido')
    }
    return render(request, 'pedidos/lista_pedidos.html', context)

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.user != pedido.cliente and \
       (request.user.tipo != 'integral' or request.user != pedido.empresa.usuario):
        messages.error(request, 'No tienes permiso para ver este pedido')
        return redirect('dashboard')
    
    context = {
        'pedido': pedido,
        'transacciones': Transaccion.objects.filter(pedido=pedido)
    }
    return render(request, 'pedidos/detalle_pedido.html', context)

@login_required
def actualizar_estado_pedido(request, pedido_id):
    if request.method != 'POST':
        return redirect('detalle_pedido', pedido_id=pedido_id)
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.user.tipo != 'integral' or request.user != pedido.empresa.usuario:
        messages.error(request, 'No tienes permiso para actualizar este pedido')
        return redirect('dashboard')
    
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Pedido.ESTADOS).keys():
        pedido.estado = nuevo_estado
        pedido.save()
        
        # Crear notificación para el cliente
        Notificacion.objects.create(
            usuario=pedido.cliente,
            tipo='pedido_actualizado',
            titulo=f'Tu pedido ha sido actualizado',
            mensaje=f'El estado de tu pedido #{pedido.id} ha cambiado a {pedido.get_estado_display()}',
            pedido=pedido
        )
        
        messages.success(request, 'Estado del pedido actualizado correctamente')
    else:
        messages.error(request, 'Estado no válido')
    
    return redirect('detalle_pedido', pedido_id=pedido_id)

@login_required
@require_POST
def eliminar_del_carrito(request):
    try:
        data = json.loads(request.body)
        item_ids = data.get('item_ids', [])
        
        if not item_ids:
            return JsonResponse({'success': False, 'error': 'No se proporcionaron IDs de ítems'})
        
        # Obtener el carrito del usuario
        carrito = get_object_or_404(Carrito, usuario=request.user)
        
        # Verificar que los ítems pertenezcan al carrito del usuario
        items = ItemCarrito.objects.filter(id__in=item_ids, carrito=carrito)
        
        if not items.exists():
            return JsonResponse({'success': False, 'error': 'No se encontraron ítems válidos para eliminar'})
        
        try:
            with transaction.atomic():
                # Restaurar el stock y eliminar los ítems
                for item in items:
                    producto = item.producto
                    producto.stock += item.cantidad
                    producto.save()
                    item.delete()
                
                # Recalcular subtotal, IVA y total
                remaining_items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
                subtotal = sum(float(item.producto.precio) * item.cantidad for item in remaining_items)
                iva = round(subtotal * 0.19, 2)
                total = round(subtotal + iva, 2)
                
                return JsonResponse({
                    'success': True,
                    'mensaje': 'Productos eliminados del carrito exitosamente',
                    'subtotal': subtotal,
                    'iva': iva,
                    'total': total
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al actualizar el carrito y el stock: {str(e)}'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al procesar la solicitud: {str(e)}'})

@role_required(['superusuario'])
def categorias(request):
    categorias = CategoriaProducto.objects.all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        if nombre:
            CategoriaProducto.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('categorias')
        else:
            messages.error(request, 'El nombre de la categoría es requerido')
    
    return render(request, 'pedidos/categorias.html', {
        'categorias': categorias
    })