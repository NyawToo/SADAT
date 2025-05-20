from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from core.decorators import empresa_integral_required
from .models import Pedido, SolicitudConfeccion
from django.views.decorators.http import require_POST
import json

@login_required
@empresa_integral_required
def lista_pedidos_empresa(request):
    empresa = request.user.microempresaintegral
    pedidos = Pedido.objects.filter(empresa=empresa).order_by('-fecha_pedido')
    return render(request, 'pedidos/lista_pedidos_empresa.html', {'pedidos': pedidos})

@login_required
@empresa_integral_required
def gestionar_solicitudes_confeccion(request):
    empresa = request.user.microempresaintegral
    solicitudes = SolicitudConfeccion.objects.filter(empresa_integral=empresa).order_by('-fecha_solicitud')
    
    estado_filtro = request.GET.get('estado')
    fecha_filtro = request.GET.get('fecha_deseada')
    
    if estado_filtro:
        solicitudes = solicitudes.filter(estado=estado_filtro)
    if fecha_filtro:
        solicitudes = solicitudes.filter(fecha_entrega_requerida=fecha_filtro)
    
    return render(request, 'pedidos/gestionar_solicitudes_confeccion.html', {
        'solicitudes': solicitudes,
        'estado_filtro': estado_filtro,
        'fecha_filtro': fecha_filtro
    })

@login_required
@empresa_integral_required
@require_POST
def cotizar_solicitud(request, solicitud_id):
    try:
        data = json.loads(request.body)
        solicitud = get_object_or_404(SolicitudConfeccion, id=solicitud_id, empresa_integral=request.user.microempresaintegral)
        
        if solicitud.estado != 'pendiente':
            return JsonResponse({'success': False, 'error': 'La solicitud no está en estado pendiente'})
        
        solicitud.precio_por_prenda = data.get('precio_por_prenda')
        solicitud.tiempo_estimado = data.get('tiempo_estimado')
        solicitud.comentarios_cotizacion = data.get('comentarios')
        solicitud.fecha_cotizacion = timezone.now()
        solicitud.estado = 'cotizada'
        solicitud.save()
        
        # Crear notificación para el cliente
        from notificaciones.models import Notificacion
        Notificacion.objects.create(
            usuario=solicitud.cliente,
            tipo='cotizacion_recibida',
            titulo='Nueva cotización recibida',
            mensaje=f'Has recibido una cotización para tu solicitud de confección #{solicitud.id}',
            prioridad='alta'
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@empresa_integral_required
@require_POST
def actualizar_estado_solicitud(request, solicitud_id):
    try:
        data = json.loads(request.body)
        solicitud = get_object_or_404(SolicitudConfeccion, id=solicitud_id, empresa_integral=request.user.microempresaintegral)
        nuevo_estado = data.get('estado')
        
        if nuevo_estado not in dict(SolicitudConfeccion.ESTADOS):
            return JsonResponse({'success': False, 'error': 'Estado no válido'})
        
        solicitud.estado = nuevo_estado
        solicitud.save()
        
        # Crear notificación para el cliente
        from notificaciones.models import Notificacion
        Notificacion.objects.create(
            usuario=solicitud.cliente,
            tipo='solicitud_actualizada',
            titulo='Actualización de solicitud',
            mensaje=f'Tu solicitud de confección #{solicitud.id} ha sido actualizada a estado: {solicitud.get_estado_display()}',
            prioridad='alta'
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@empresa_integral_required
def actualizar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, empresa=request.user.microempresaintegral)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        # Use states defined in the model for validation
        estados_validos = [estado[0] for estado in Pedido.ESTADOS]
        
        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
            pedido.save()
            
            # Crear notificación para el cliente
            from notificaciones.models import Notificacion
            Notificacion.objects.create(
                usuario=pedido.cliente,
                tipo='pedido_actualizado',
                titulo='Actualización de pedido',
                mensaje=f'Tu pedido #{pedido.id} ha sido actualizado a estado: {pedido.get_estado_display()}', # Use get_estado_display for user-friendly name
                prioridad='alta'
            )
            
            messages.success(request, 'Estado del pedido actualizado correctamente')
        else:
            messages.error(request, 'Estado no válido')
    
    # Redirect to the main management view for consistency
    return redirect('gestionar_pedidos')