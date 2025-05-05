from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from core.decorators import role_required
from empresas.models import MicroempresaIntegral, MicroempresaSatelite, ProductoTerminado
from pedidos.models import Pedido, DetallePedido
import pandas as pd
import matplotlib.pyplot as plt
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

@login_required
@role_required(['cliente'])
def reporte_cliente(request):
    # Obtener el primer día del mes actual
    primer_dia_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Obtener compras del mes actual agrupadas por empresa
    compras_mes = Pedido.objects.filter(
        cliente=request.user,
        fecha_creacion__gte=primer_dia_mes
    ).values(
        'empresa_integral__nombre',
        'empresa_integral__id'
    ).annotate(
        total_compras=Count('id'),
        monto_total=Sum('total'),
        productos_comprados=Count('itempedido__producto', distinct=True)
    ).order_by('-total_compras')  # Ordenar por cantidad de compras

    # Preparar datos para el gráfico
    empresas_labels = [compra['empresa_integral__nombre'] for compra in compras_mes]
    montos_totales = [float(compra['monto_total']) for compra in compras_mes]

    # Obtener detalles de todas las compras
    detalles_compras = []
    for compra in compras_mes:
        ultimo_pedido = Pedido.objects.filter(
            cliente=request.user,
            empresa_integral_id=compra['empresa_integral__id']
        ).order_by('-fecha_creacion').first()

        detalles_compras.append({
            'empresa': compra['empresa_integral__nombre'],
            'tipo': 'Integral',
            'productos_comprados': DetallePedido.objects.filter(
                pedido__cliente=request.user,
                pedido__empresa_integral_id=compra['empresa_integral__id'],
                pedido__fecha_creacion__gte=primer_dia_mes
            ).count(),
            'total_pedidos': compra['total_compras'],
            'ultima_compra': ultimo_pedido.fecha_creacion if ultimo_pedido else None,
            'estado_ultimo_pedido': ultimo_pedido.get_estado_display() if ultimo_pedido else 'N/A',
            'estado_color': 'success' if ultimo_pedido and ultimo_pedido.estado == 'completado' else 'warning',
            'monto_total': compra['monto_total']
        })

    return render(request, 'reportes/reporte_cliente.html', {
        'empresas_mas_compradas': compras_mes,
        'detalles_compras': detalles_compras,
        'empresas_labels': empresas_labels,
        'montos_totales': montos_totales
    })

@login_required
@role_required(['empresa_integral', 'empresa_satelite', 'superusuario'])
def reporte_empresa(request, empresa_id=None):
    # Si el usuario es superusuario y se proporciona empresa_id
    if request.user.tipo == 'superusuario' and empresa_id:
        empresa = get_object_or_404(MicroempresaIntegral, id=empresa_id)
    # Si es usuario de empresa y no se proporciona empresa_id
    elif empresa_id is None and (hasattr(request.user, 'empresa_integral') or hasattr(request.user, 'empresa_satelite')):
        es_integral = hasattr(request.user, 'empresa_integral')
        empresa = request.user.empresa_integral if es_integral else request.user.empresa_satelite
    # Si es usuario de empresa pero se proporciona un empresa_id diferente
    else:
        return HttpResponse('No tiene permisos para ver los reportes de esta empresa', status=403)
    
    es_integral = isinstance(empresa, MicroempresaIntegral)
    
    # Obtener el primer día del mes actual
    primer_dia_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Obtener el primer y último día del año actual
    año_actual = timezone.now().year
    primer_dia_año = datetime(año_actual, 1, 1, tzinfo=ZoneInfo("UTC"))
    ultimo_dia_año = datetime(año_actual, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("UTC"))

    # Productos más vendidos
    if es_integral:
        productos_vendidos = DetallePedido.objects.filter(
            pedido__empresa_integral=empresa,
            pedido__fecha_creacion__gte=primer_dia_mes
        ).values(
            'producto__nombre'
        ).annotate(
            cantidad_vendida=Sum('cantidad'),
            ingresos=Sum(F('cantidad') * F('precio_unitario'))
        ).order_by('-cantidad_vendida')
    else:
        productos_vendidos = Pedido.objects.filter(
            empresa_satelite=empresa,
            fecha_creacion__gte=primer_dia_mes
        ).values(
            'estado'
        ).annotate(
            cantidad=Count('id')
        )

    # Estados de pedidos
    estados_pedidos = Pedido.objects.filter(
        **{'empresa_integral' if es_integral else 'empresa_satelite': empresa},
        fecha_creacion__gte=primer_dia_mes
    ).values('estado').annotate(cantidad=Count('id'))

    total_pedidos = sum(estado['cantidad'] for estado in estados_pedidos)
    estados_data = [{
        'nombre': Pedido.ESTADOS_DICT.get(estado['estado'], estado['estado']),
        'cantidad': estado['cantidad'],
        'porcentaje': round((estado['cantidad'] / total_pedidos) * 100 if total_pedidos > 0 else 0, 2),
        'color': 'success' if estado['estado'] == 'completado' else 'warning'
    } for estado in estados_pedidos]

    # Preparar datos para gráficos
    productos_labels = [p['producto__nombre'] for p in productos_vendidos[:5]] if es_integral else []
    productos_cantidades = [p['cantidad_vendida'] for p in productos_vendidos[:5]] if es_integral else []
    estados_labels = [estado['nombre'] for estado in estados_data]
    estados_cantidades = [estado['cantidad'] for estado in estados_data]
    estados_colores = ['#28a745' if estado['nombre'] == 'Completado' else '#ffc107' for estado in estados_data]

    # Obtener pedidos recientes
    pedidos = Pedido.objects.filter(
        **{'empresa_integral' if es_integral else 'empresa_satelite': empresa},
        fecha_creacion__gte=primer_dia_mes
    ).order_by('-fecha_creacion')[:10]

    pedidos_data = [{
        'id': pedido.id,
        'cliente': pedido.cliente.get_full_name(),
        'productos': ', '.join([f"{item.cantidad}x {item.producto.nombre}" for item in pedido.itempedido_set.all()]),
        'fecha': pedido.fecha_creacion,
        'estado': pedido.get_estado_display(),
        'estado_color': 'success' if pedido.estado == 'completado' else 'warning',
        'total': pedido.total
    } for pedido in pedidos]

    return render(request, 'reportes/reporte_empresa.html', {
        'empresa': empresa,
        'productos_mas_vendidos': productos_vendidos[:5] if es_integral else [],
        'estados_pedidos': estados_data,
        'pedidos': pedidos_data,
        'productos_labels': productos_labels,
        'productos_cantidades': productos_cantidades,
        'estados_labels': estados_labels,
        'estados_cantidades': estados_cantidades,
        'estados_colores': estados_colores
    })

@login_required
@role_required(['superusuario'])
def panel_admin_reportes(request):
    from django.db.models import Q
    
    # Obtener el primer y último día del año actual
    año_actual = timezone.now().year
    primer_dia_año = datetime(año_actual, 1, 1, tzinfo=ZoneInfo("UTC"))
    ultimo_dia_año = datetime(año_actual, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("UTC"))
    
    # Empresas Integrales
    empresas_integrales = MicroempresaIntegral.objects.all().annotate(
        total_ventas_anual=Sum(
            'pedidos__total',
            filter=Q(pedidos__fecha_pedido__gte=primer_dia_año, pedidos__fecha_pedido__lte=ultimo_dia_año)
        ),
        productos_activos=Count('productoterminado', distinct=True),
        pedidos_pendientes=Count(
            'pedidos',
            filter=Q(pedidos__estado__in=['pendiente', 'en_produccion'])
        ),
        productos_vendidos=Count(
            'pedidos__producto',
            filter=Q(pedidos__fecha_pedido__gte=primer_dia_año, pedidos__fecha_pedido__lte=ultimo_dia_año),
            distinct=True
        )
    )

    # Empresas Satélites
    empresas_satelites = MicroempresaSatelite.objects.all().annotate(
        total_pedidos_anual=Count(
            'solicitudconfeccion',
            filter=Q(solicitudconfeccion__fecha_solicitud__year=timezone.now().year)
        ),
        pedidos_en_proceso=Count(
            'solicitudconfeccion',
            filter=Q(solicitudconfeccion__estado='en_proceso')
        ),
        pedidos_completados=Count(
            'solicitudconfeccion',
            filter=Q(solicitudconfeccion__estado='completada')
        )
    )

    return render(request, 'reportes/panel_admin_reportes.html', {
        'empresas_integrales': empresas_integrales,
        'empresas_satelites': empresas_satelites
    })

def exportar_reporte(request, tipo_reporte, formato, **kwargs):
    if tipo_reporte == 'cliente':
        data = generar_datos_reporte_cliente(request.user)
    elif tipo_reporte == 'empresa':
        empresa_id = kwargs.get('empresa_id')
        empresa = get_object_or_404(MicroempresaIntegral, id=empresa_id)
        es_integral = isinstance(empresa, MicroempresaIntegral)
        data = {
            'productos_vendidos': pd.DataFrame(list(productos_vendidos)) if es_integral else pd.DataFrame(),
            'estados_pedidos': pd.DataFrame(list(estados_pedidos)),
            'pedidos': pd.DataFrame(list(pedidos_data))
        }
    else:
        return HttpResponse('Tipo de reporte no válido', status=400)

    if formato == 'excel':
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()
        output.seek(0)
        response = HttpResponse(output.read(),
                              content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={tipo_reporte}_reporte.xlsx'
        return response

    elif formato == 'pdf':
        # Crear un PDF con reportlab
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={tipo_reporte}_reporte.pdf'
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        
        # Agregar título
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f'Reporte de {tipo_reporte.title()}', styles['Title']))
        
        # Agregar tablas de datos
        for name, df in data.items():
            elements.append(Paragraph(name.replace('_', ' ').title(), styles['Heading1']))
            if not df.empty:
                table_data = [df.columns.tolist()] + df.values.tolist()
                t = Table(table_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(t)
        
        doc.build(elements)
        return response

    elif formato == 'png':
        # Crear un gráfico con matplotlib
        plt.figure(figsize=(12, 6))
        
        if 'productos_vendidos' in data and not data['productos_vendidos'].empty:
            plt.subplot(1, 2, 1)
            data['productos_vendidos'].plot(kind='bar')
            plt.title('Productos más vendidos')
            plt.xticks(rotation=45)
        
        if 'estados_pedidos' in data and not data['estados_pedidos'].empty:
            plt.subplot(1, 2, 2)
            data['estados_pedidos'].plot(kind='pie', y='cantidad')
            plt.title('Estados de pedidos')
        
        plt.tight_layout()
        
        # Guardar el gráfico en un buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename={tipo_reporte}_reporte.png'
        return response

    return HttpResponse('Formato no soportado', status=400)