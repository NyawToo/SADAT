from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import SolicitudConfeccion
from empresas.models import MicroempresaIntegral, MicroempresaSatelite
import json


@login_required
@require_POST
def cotizar_solicitud_universal(request, solicitud_id):
    """
    Vista universal para cotizar solicitudes de confección.
    Funciona tanto para empresas integrales como satélites.
    """
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Detectar tipo de empresa y obtener la solicitud correspondiente
        if user.tipo == 'integral':
            try:
                empresa = MicroempresaIntegral.objects.get(usuario=user)
                solicitud = get_object_or_404(SolicitudConfeccion, id=solicitud_id, empresa_integral=empresa)
            except MicroempresaIntegral.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No se encontró la empresa integral'}, status=404)
                
        elif user.tipo == 'satelite':
            try:
                empresa = MicroempresaSatelite.objects.get(usuario=user)
                solicitud = get_object_or_404(SolicitudConfeccion, id=solicitud_id, empresa_satelite=empresa)
            except MicroempresaSatelite.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No se encontró la empresa satélite'}, status=404)
        else:
            return JsonResponse({'success': False, 'error': 'Solo las empresas pueden cotizar solicitudes'}, status=403)
        
        # Validar que la solicitud esté en estado pendiente
        if solicitud.estado != 'pendiente':
            return JsonResponse({'success': False, 'error': 'La solicitud no está en estado pendiente'})
        
        # Obtener datos de la cotización
        precio_por_prenda = data.get('precio_por_prenda')
        tiempo_estimado = data.get('tiempo_estimado')
        comentarios = data.get('comentarios', '')
        
        if not precio_por_prenda or not tiempo_estimado:
            return JsonResponse({'success': False, 'error': 'Faltan datos requeridos'})
        
        try:
            # Actualizar la solicitud con la cotización
            precio_total = float(precio_por_prenda) * solicitud.cantidad_prendas
            solicitud.precio_por_prenda = float(precio_por_prenda)
            solicitud.tiempo_estimado = int(tiempo_estimado)
            solicitud.comentarios_cotizacion = comentarios
            solicitud.cotizacion = precio_total
            solicitud.fecha_cotizacion = timezone.now()
            solicitud.estado = 'cotizada'
            solicitud.save()
            
            # Crear notificación para el cliente
            from notificaciones.models import Notificacion
            
            # Obtener el nombre de la empresa (ambos usan nombre_empresa)
            nombre_empresa = empresa.nombre_empresa
            
            Notificacion.objects.create(
                usuario=solicitud.cliente,
                tipo='cotizacion_recibida',
                titulo='Nueva cotización recibida',
                mensaje=f'Has recibido una cotización para tu solicitud de confección #{solicitud.id} de {nombre_empresa}. '
                        f'Precio total: ${precio_total}, Tiempo estimado: {tiempo_estimado} días',
                prioridad='alta'
            )
            
            return JsonResponse({'success': True})
            
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Datos inválidos. Verifique precio y tiempo'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato de datos inválido'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al procesar la solicitud: {str(e)}'})


@login_required
@require_POST
def actualizar_estado_solicitud_universal(request, solicitud_id):
    """
    Vista universal para actualizar el estado de solicitudes de confección.
    Funciona tanto para empresas integrales como satélites.
    """
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Detectar tipo de empresa y obtener la solicitud correspondiente
        if user.tipo == 'integral':
            try:
                empresa = MicroempresaIntegral.objects.get(usuario=user)
                solicitud = get_object_or_404(SolicitudConfeccion, id=solicitud_id, empresa_integral=empresa)
            except MicroempresaIntegral.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No se encontró la empresa integral'}, status=404)
                
        elif user.tipo == 'satelite':
            try:
                empresa = MicroempresaSatelite.objects.get(usuario=user)
                solicitud = get_object_or_404(SolicitudConfeccion, id=solicitud_id, empresa_satelite=empresa)
            except MicroempresaSatelite.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No se encontró la empresa satélite'}, status=404)
        else:
            return JsonResponse({'success': False, 'error': 'Solo las empresas pueden actualizar solicitudes'}, status=403)
        
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
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato de datos inválido'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
