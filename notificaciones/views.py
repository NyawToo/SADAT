from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Notificacion
from django.db.models import Q

@login_required
def log_notificaciones(request):
    filtros = {
        'fecha_inicio': request.GET.get('fecha_inicio'),
        'fecha_fin': request.GET.get('fecha_fin'),
        'tipo': request.GET.get('tipo'),
        'estado': request.GET.get('estado')
    }
    
    query = Q()
    
    if filtros['fecha_inicio']:
        query &= Q(fecha_creacion__gte=filtros['fecha_inicio'])
    if filtros['fecha_fin']:
        query &= Q(fecha_creacion__lte=filtros['fecha_fin'])
    if filtros['tipo']:
        query &= Q(tipo=filtros['tipo'])
    if filtros['estado']:
        query &= Q(estado=filtros['estado'])
    
    notificaciones = Notificacion.objects.filter(query).order_by('-fecha_creacion')
    
    return render(request, 'notificaciones/log_notificaciones.html', {
        'notificaciones': notificaciones,
        'filtros': filtros
    })

def reintentar_envio(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)
    # Aquí iría la lógica para reintentar el envío
    return redirect('log_notificaciones')

def limpiar_registros(request):
    # Aquí iría la lógica para limpiar registros antiguos
    return redirect('log_notificaciones')
