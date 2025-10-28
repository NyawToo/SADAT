from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from core.decorators import role_required
from core.models import Usuario
from empresas.models import MicroempresaIntegral, MicroempresaSatelite
from pedidos.models import Pedido
from .models import Queja
import json

@login_required
@role_required(['superusuario'])
def reporte_global(request):
    # Obtener fechas para filtros
    primer_dia_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    año_actual = timezone.now().year
    primer_dia_año = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Estadísticas generales
    total_empresas_integrales = MicroempresaIntegral.objects.count()
    total_empresas_satelites = MicroempresaSatelite.objects.count()
    total_empresas = total_empresas_integrales + total_empresas_satelites
    
    # Ventas totales
    ventas_totales = Pedido.objects.aggregate(
        total=Sum('total')
    )['total'] or 0
    
    ventas_mes = Pedido.objects.filter(
        fecha_pedido__gte=primer_dia_mes
    ).aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Pedidos
    pedidos_totales = Pedido.objects.count()
    pedidos_completados = Pedido.objects.filter(estado='entregado').count()
    
    # Usuarios
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    usuarios_nuevos = Usuario.objects.filter(
        date_joined__gte=primer_dia_mes
    ).count()
    
    # Estadísticas resumidas
    estadisticas = {
        'total_empresas': total_empresas,
        'empresas_activas': total_empresas,  # Asumiendo que todas están activas
        'ventas_totales': f'${ventas_totales:,.2f}',
        'ventas_mes': f'{ventas_mes:,.2f}',
        'pedidos_totales': pedidos_totales,
        'pedidos_completados': pedidos_completados,
        'usuarios_activos': usuarios_activos,
        'usuarios_nuevos': usuarios_nuevos
    }
    
    # Ranking de empresas integrales
    ranking_empresas = []
    
    empresas_integrales = MicroempresaIntegral.objects.annotate(
        ventas_totales=Sum('pedidos__total', filter=Q(pedidos__estado='entregado')),
        pedidos_completados=Count('pedidos', filter=Q(pedidos__estado='entregado')),
        total_pedidos=Count('pedidos'),
        productos_activos=Count('productoterminado', distinct=True)
    ).order_by('-ventas_totales')
    
    for empresa in empresas_integrales:
        # Calcular valoración basada en múltiples factores
        pedidos_completados = empresa.pedidos_completados or 0
        total_pedidos = empresa.total_pedidos or 1  # Evitar división por cero
        productos_activos = empresa.productos_activos or 0
        ventas = float(empresa.ventas_totales or 0)
        
        # Factores de valoración:
        # - Tasa de completación de pedidos (40%)
        # - Cantidad de productos activos (30%)
        # - Cantidad de pedidos completados (30%)
        tasa_completacion = (pedidos_completados / total_pedidos) * 40 if total_pedidos > 0 else 0
        factor_productos = min(30, productos_activos * 5)  # Máximo 30 puntos
        factor_pedidos = min(30, pedidos_completados * 3)  # Máximo 30 puntos
        
        # Valoración final (mínimo 10 si la empresa está activa)
        valoracion = max(10, int(tasa_completacion + factor_productos + factor_pedidos))
        
        ranking_empresas.append({
            'nombre': empresa.nombre_empresa,
            'tipo': 'Integral',
            'ventas_totales': f'{ventas:,.2f}',
            'pedidos_completados': pedidos_completados,
            'valoracion': valoracion
        })
    
    # Agregar empresas satélites al ranking
    empresas_satelites = MicroempresaSatelite.objects.annotate(
        total_solicitudes=Count('solicitudconfeccion'),
        solicitudes_completadas=Count('solicitudconfeccion', filter=Q(solicitudconfeccion__estado='completada')),
        solicitudes_en_proceso=Count('solicitudconfeccion', filter=Q(solicitudconfeccion__estado='en_proceso')),
        ingresos_totales=Sum('solicitudconfeccion__cotizacion', filter=Q(solicitudconfeccion__estado='completada'))
    ).order_by('-solicitudes_completadas')
    
    for empresa in empresas_satelites:
        # Calcular valoración para satélites
        total_solicitudes = empresa.total_solicitudes or 1
        completadas = empresa.solicitudes_completadas or 0
        en_proceso = empresa.solicitudes_en_proceso or 0
        ingresos = float(empresa.ingresos_totales or 0)
        
        # Factores:
        # - Tasa de completación (50%)
        # - Solicitudes completadas (30%)
        # - Solicitudes en proceso (20%)
        tasa_completacion = (completadas / total_solicitudes) * 50 if total_solicitudes > 0 else 0
        factor_completadas = min(30, completadas * 3)
        factor_en_proceso = min(20, en_proceso * 2)
        
        # Valoración final (mínimo 10 si la empresa está activa)
        valoracion = max(10, int(tasa_completacion + factor_completadas + factor_en_proceso))
        
        ranking_empresas.append({
            'nombre': empresa.nombre_empresa,
            'tipo': 'Satélite',
            'ventas_totales': f'{ingresos:,.2f}',
            'pedidos_completados': completadas,
            'valoracion': valoracion
        })
    
    # Ordenar ranking por valoración (descendente), luego por pedidos completados
    ranking_empresas = sorted(ranking_empresas, key=lambda x: (x['valoracion'], x['pedidos_completados']), reverse=True)
    
    # Aplicar paginación al ranking
    paginator = Paginator(ranking_empresas, 15)  # 15 empresas por página
    page_number = request.GET.get('page', 1)
    ranking_empresas_paginado = paginator.get_page(page_number)
    
    # Datos para gráficos
    # Tendencia de ventas (últimos 6 meses)
    ventas_por_mes = []
    meses_labels = []
    
    for i in range(6):
        fecha = timezone.now() - timedelta(days=30 * i)
        primer_dia = fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            ultimo_dia = timezone.now()
        else:
            ultimo_dia = (primer_dia + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        ventas = Pedido.objects.filter(
            fecha_pedido__gte=primer_dia,
            fecha_pedido__lte=ultimo_dia
        ).aggregate(total=Sum('total'))['total'] or 0
        
        ventas_por_mes.insert(0, float(ventas))
        meses_labels.insert(0, fecha.strftime('%B'))
    
    # Distribución por tipo de empresa
    distribucion_empresas = {
        'labels': ['Integrales', 'Satélites'],
        'data': [total_empresas_integrales, total_empresas_satelites]
    }
    
    # Métricas de rendimiento
    pedidos_con_fecha_entrega = Pedido.objects.filter(
        estado='entregado',
        fecha_pedido__isnull=False
    )
    
    # Calcular tiempo promedio (simplificado - usando 5 días como ejemplo)
    tiempo_promedio = 5 if pedidos_con_fecha_entrega.count() > 0 else 0
    
    # Tasa de satisfacción (pedidos completados / total de pedidos)
    tasa_satisfaccion = round((pedidos_completados / pedidos_totales * 100) if pedidos_totales > 0 else 0, 2)
    
    # Tasa de conversión (pedidos completados vs pendientes)
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    tasa_conversion = round((pedidos_completados / (pedidos_completados + pedidos_pendientes) * 100) if (pedidos_completados + pedidos_pendientes) > 0 else 0, 2)
    
    # Ticket promedio
    ticket_promedio = round(ventas_totales / pedidos_totales if pedidos_totales > 0 else 0, 2)
    
    metricas = {
        'tiempo_promedio_entrega': tiempo_promedio,
        'tasa_satisfaccion': tasa_satisfaccion,
        'tasa_conversion': tasa_conversion,
        'ticket_promedio': f'{ticket_promedio:,.2f}'
    }
    
    # Alertas y notificaciones
    alertas = []
    
    # Alerta por pedidos pendientes
    if pedidos_pendientes > 10:
        alertas.append({
            'tipo': 'urgente',
            'titulo': 'Pedidos Pendientes',
            'mensaje': f'Hay {pedidos_pendientes} pedidos pendientes de procesar',
            'fecha': timezone.now().strftime('%d/%m/%Y')
        })
    
    # Alerta por ventas bajas del mes
    if ventas_mes < (ventas_totales / 12):  # Si las ventas del mes son menores al promedio mensual
        alertas.append({
            'tipo': 'advertencia',
            'titulo': 'Ventas Bajas',
            'mensaje': 'Las ventas de este mes están por debajo del promedio',
            'fecha': timezone.now().strftime('%d/%m/%Y')
        })
    
    # Alerta por nuevos usuarios
    if usuarios_nuevos > 5:
        alertas.append({
            'tipo': 'info',
            'titulo': 'Nuevos Usuarios',
            'mensaje': f'{usuarios_nuevos} nuevos usuarios se han registrado este mes',
            'fecha': timezone.now().strftime('%d/%m/%Y')
        })
    
    context = {
        'estadisticas': estadisticas,
        'ranking_empresas': ranking_empresas_paginado,
        'labels_ventas': json.dumps(meses_labels),
        'datos_ventas': json.dumps(ventas_por_mes),
        'distribucion_empresas_labels': json.dumps(distribucion_empresas['labels']),
        'distribucion_empresas_data': json.dumps(distribucion_empresas['data']),
        'metricas': metricas,
        'alertas': alertas
    }
    
    return render(request, 'reportes/reporte_global.html', context)

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
