from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import stripe
from .models import Transaccion
from django.db.models import Q
from pedidos.models import Carrito, ItemCarrito, Pedido
from core.decorators import role_required
from .services import StripeService
from .stripe_config import PAYMENT_STATUS, STRIPE_WEBHOOK_SECRET

@login_required
def ejecucion_pago(request):
    carrito_obj, created = Carrito.objects.get_or_create(usuario=request.user)
    items_carrito = ItemCarrito.objects.filter(carrito=carrito_obj).select_related('producto')
    
    if not items_carrito.exists():
        messages.error(request, 'Tu carrito está vacío')
        return redirect('ver_carrito')
    
    # Calcular subtotal por producto y totales
    for item in items_carrito:
        item.subtotal = float(item.producto.precio) * item.cantidad
    
    subtotal = sum(item.subtotal for item in items_carrito)
    iva = round(subtotal * 0.19, 2)
    total = round(subtotal + iva, 2)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear el pedido
                pedido = Pedido.objects.create(
                    cliente=request.user,
                    empresa=items_carrito.first().producto.empresa,
                    producto=items_carrito.first().producto,
                    cantidad=sum(item.cantidad for item in items_carrito),
                    fecha_entrega=timezone.now().date(),
                    estado='pendiente',
                    total=total
                )
                
                # Crear la transacción
                transaccion = Transaccion.objects.create(
                    usuario=request.user,
                    monto=total,
                    estado='pendiente',
                    tipo_transaccion='pedido_estandar',
                    pedido=pedido,
                    metodo_pago=request.POST.get('metodo_pago')
                )
                
                # Procesar el pago según el método seleccionado
                metodo_pago = request.POST.get('metodo_pago')
                
                if metodo_pago == 'card':
                    # Crear sesión de Checkout de Stripe
                    session = StripeService.create_checkout_session(transaccion)
                    # Limpiar el carrito después de crear la sesión de pago
                    items_carrito.delete()
                    carrito_obj.delete()
                    return redirect(session.url)
                else:
                    # Para transferencia bancaria
                    transaccion.estado = PAYMENT_STATUS['PENDING']
                    transaccion.save()
                    # Limpiar el carrito después de actualizar la transacción
                    items_carrito.delete()
                    carrito_obj.delete()
                    messages.success(request, 'Pedido creado exitosamente')
                    return redirect('confirmar_pago', transaccion_id=transaccion.id)
                
        except Exception as e:
            messages.error(request, f'Error al procesar el pedido: {str(e)}')
            return redirect('ver_carrito')
    
    # Obtener los datos del usuario para pre-llenar el formulario
    context = {
        'items_carrito': items_carrito,
        'subtotal': round(subtotal, 2),
        'iva': iva,
        'total': total,
        'direccion_usuario': request.user.direccion if hasattr(request.user, 'direccion') else '',
        'telefono_usuario': request.user.telefono if hasattr(request.user, 'telefono') else ''
    }
    return render(request, 'pagos/ejecucion_pago.html',context)

@login_required
def confirmar_pago(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, id=transaccion_id, usuario=request.user)
    
    # Verificar si el pago ya fue procesado
    if transaccion.estado == PAYMENT_STATUS['COMPLETED']:
        messages.info(request, 'Este pago ya ha sido procesado')
        return render(request, 'pagos/resultado_pago.html', {'transaccion': transaccion})
    
    if request.method == 'POST':
        try:
            # Si es pago con tarjeta y tiene un PaymentIntent
            if transaccion.metodo_pago == 'card' and transaccion.stripe_payment_intent_id:
                # Confirmar el pago en Stripe
                payment_intent = StripeService.confirm_payment(transaccion)
                
                # Actualizar el estado del pedido
                pedido = transaccion.pedido
                pedido.estado = 'en_proceso'
                pedido.save()
                
                transaccion.estado = PAYMENT_STATUS['COMPLETED']
                transaccion.save()
                
                messages.success(request, 'Pago procesado exitosamente')
                return redirect('mis_pedidos')
            else:
                # Para transferencia bancaria, solo actualizamos el estado
                transaccion.estado = PAYMENT_STATUS['COMPLETED']
                transaccion.save()
                
                # Actualizar el estado del pedido
                pedido = transaccion.pedido
                pedido.estado = 'en_proceso'
                pedido.save()
                
                messages.success(request, 'Pago registrado exitosamente')
                return redirect('mis_pedidos')
            
        except Exception as e:
            transaccion.estado = PAYMENT_STATUS['FAILED']
            transaccion.save()
            messages.error(request, f'Error al procesar el pago: {str(e)}')
            return render(request, 'pagos/resultado_pago.html', {'transaccion': transaccion})
    
    return render(request, 'pagos/confirmar_pago.html', {'transaccion': transaccion})

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Webhook para recibir eventos de Stripe
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Verificar la firma del webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        # Manejar diferentes tipos de eventos
        if event.type == 'payment_intent.succeeded':
            # Pago exitoso
            payment_intent = event.data.object
            transaccion = Transaccion.objects.filter(
                stripe_payment_intent_id=payment_intent.id
            ).first()
            
            if transaccion:
                transaccion.estado = PAYMENT_STATUS['COMPLETED']
                transaccion.detalles_pago = {
                    'payment_intent': payment_intent.id,
                    'status': payment_intent.status,
                    'payment_method': payment_intent.payment_method
                }
                transaccion.save()
                
                # Actualizar el estado del pedido
                if transaccion.pedido:
                    pedido = transaccion.pedido
                    pedido.estado = 'en_proceso'
                    pedido.save()
        
        elif event.type == 'payment_intent.payment_failed':
            # Pago fallido
            payment_intent = event.data.object
            transaccion = Transaccion.objects.filter(
                stripe_payment_intent_id=payment_intent.id
            ).first()
            
            if transaccion:
                transaccion.estado = PAYMENT_STATUS['FAILED']
                transaccion.detalles_pago = {
                    'error': payment_intent.last_payment_error.message if payment_intent.last_payment_error else 'Pago fallido'
                }
                transaccion.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@role_required(['superusuario'])
def supervisar_pagos(request):
    filtros = {
        'fecha_inicio': request.GET.get('fecha_inicio'),
        'fecha_fin': request.GET.get('fecha_fin'),
        'estado': request.GET.get('estado'),
        'metodo_pago': request.GET.get('metodo_pago'),
        'monto_min': request.GET.get('monto_min'),
        'monto_max': request.GET.get('monto_max')
    }
    
    query = Q()
    
    if filtros['fecha_inicio']:
        query &= Q(fecha_creacion__gte=filtros['fecha_inicio'])
    if filtros['fecha_fin']:
        query &= Q(fecha_creacion__lte=filtros['fecha_fin'])
    if filtros['estado']:
        query &= Q(estado=filtros['estado'])
    if filtros['metodo_pago']:
        query &= Q(metodo_pago=filtros['metodo_pago'])
    
    transacciones = Transaccion.objects.filter(query).order_by('-fecha_creacion')
    
    return render(request, 'pagos/supervisar_pagos.html', {
        'transacciones': transacciones,
        'filtros': filtros
    })

@login_required
def ver_pagos_recibidos(request):
    filtros = {
        'fecha_inicio': request.GET.get('fecha_inicio'),
        'fecha_fin': request.GET.get('fecha_fin'),
        'estado': request.GET.get('estado')
    }
    
    query = Q(usuario=request.user)
    
    if filtros['fecha_inicio']:
        query &= Q(fecha_creacion__gte=filtros['fecha_inicio'])
    if filtros['fecha_fin']:
        query &= Q(fecha_creacion__lte=filtros['fecha_fin'])
    if filtros['estado']:
        query &= Q(estado=filtros['estado'])
    
    transacciones = Transaccion.objects.filter(query).order_by('-fecha_creacion')
    
    return render(request, 'pagos/ver_pagos_recibidos.html', {
        'transacciones': transacciones,
        'filtros': filtros
    })
