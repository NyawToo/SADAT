from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SolicitudConfeccion
from empresas.models import MicroempresaIntegral, MicroempresaSatelite
import datetime


@login_required
def gestionar_solicitudes_confeccion_universal(request):
    """
    Vista universal para gestionar solicitudes de confección.
    Funciona tanto para empresas integrales como satélites.
    """
    user = request.user
    
    # Detectar tipo de empresa y filtrar solicitudes correspondientes
    if user.tipo == 'integral':
        try:
            empresa = MicroempresaIntegral.objects.get(usuario=user)
            solicitudes = SolicitudConfeccion.objects.filter(empresa_integral=empresa).order_by('-fecha_solicitud')
        except MicroempresaIntegral.DoesNotExist:
            messages.error(request, 'No se encontró la empresa integral')
            return redirect('home')
            
    elif user.tipo == 'satelite':
        try:
            empresa = MicroempresaSatelite.objects.get(usuario=user)
            solicitudes = SolicitudConfeccion.objects.filter(empresa_satelite=empresa).order_by('-fecha_solicitud')
        except MicroempresaSatelite.DoesNotExist:
            messages.error(request, 'No se encontró la empresa satélite')
            return redirect('home')
    else:
        messages.error(request, 'No tiene permisos para acceder a esta página')
        return redirect('home')
    
    # Aplicar filtros si existen
    estado_filtro = request.GET.get('estado')
    fecha_filtro = request.GET.get('fecha_deseada')
    
    if estado_filtro:
        solicitudes = solicitudes.filter(estado=estado_filtro)
        
    if fecha_filtro:
        try:
            fecha_obj = datetime.datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            solicitudes = solicitudes.filter(fecha_entrega_requerida=fecha_obj)
        except (ValueError, TypeError):
            messages.error(request, 'Formato de fecha inválido')
    
    return render(request, 'pedidos/gestionar_solicitudes_confeccion.html', {
        'solicitudes': solicitudes,
        'estado_filtro': estado_filtro,
        'fecha_filtro': fecha_filtro
    })
