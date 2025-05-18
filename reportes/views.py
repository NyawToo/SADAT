from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.decorators import role_required
from .models import Queja
from django.utils import timezone
from django.db.models import Q

@login_required
def reporte_global(request):
    return render(request, 'reportes/reporte_global.html')

@login_required
def reporte_ventas(request):
    return render(request, 'reportes/reporte_ventas.html')

@role_required(['superusuario'])
def quejas(request):
    filtros = {
        'fecha_inicio': request.GET.get('fecha_inicio'),
        'fecha_fin': request.GET.get('fecha_fin'),
        'estado': request.GET.get('estado'),
        'tipo': request.GET.get('tipo')
    }
    
    query = Q()
    
    if filtros['fecha_inicio']:
        query &= Q(fecha_creacion__gte=filtros['fecha_inicio'])
    if filtros['fecha_fin']:
        query &= Q(fecha_creacion__lte=filtros['fecha_fin'])
    if filtros['estado']:
        query &= Q(estado=filtros['estado'])
    if filtros['tipo']:
        query &= Q(tipo=filtros['tipo'])
    
    quejas = Queja.objects.filter(query).order_by('-fecha_creacion')
    
    if request.method == 'POST':
        queja_id = request.POST.get('queja_id')
        accion = request.POST.get('accion')
        
        try:
            queja = Queja.objects.get(id=queja_id)
            if accion == 'resolver':
                queja.estado = 'resuelta'
                queja.fecha_resolucion = timezone.now()
                messages.success(request, 'Queja marcada como resuelta')
            elif accion == 'en_proceso':
                queja.estado = 'en_proceso'
                messages.success(request, 'Queja marcada como en proceso')
            queja.save()
        except Queja.DoesNotExist:
            messages.error(request, 'Queja no encontrada')
    
    return render(request, 'reportes/quejas.html', {
        'quejas': quejas,
        'filtros': filtros
    })
