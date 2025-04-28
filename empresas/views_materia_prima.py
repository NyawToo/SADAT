from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg, F
from django.db.models.functions import TruncMonth
from .models_materia_prima import CategoriaMateriaPrima, MateriaPrima, MovimientoMateriaPrima
from core.decorators import empresa_integral_required

@login_required
@empresa_integral_required
def gestionar_categorias_materia_prima(request):
    empresa = request.user.microempresaintegral
    categorias = CategoriaMateriaPrima.objects.filter(empresa=empresa)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria_id = request.POST.get('categoria_id')

        if categoria_id:  # Editar categoría existente
            categoria = get_object_or_404(CategoriaMateriaPrima, id=categoria_id, empresa=empresa)
            categoria.nombre = nombre
            categoria.descripcion = descripcion
            categoria.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
        else:  # Crear nueva categoría
            CategoriaMateriaPrima.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                empresa=empresa
            )
            messages.success(request, 'Categoría creada exitosamente.')

        return redirect('gestionar_categorias_materia_prima')

    return render(request, 'empresas/materia_prima/categorias.html', {
        'categorias': categorias
    })

@login_required
@empresa_integral_required
def gestionar_materia_prima(request):
    empresa = request.user.microempresaintegral
    materias_primas = MateriaPrima.objects.filter(empresa=empresa)
    categorias = CategoriaMateriaPrima.objects.filter(empresa=empresa)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria_id = request.POST.get('categoria')
        cantidad = request.POST.get('cantidad')
        unidad_medida = request.POST.get('unidad_medida')
        precio_unitario = request.POST.get('precio_unitario')
        stock_minimo = request.POST.get('stock_minimo')
        materia_prima_id = request.POST.get('materia_prima_id')

        categoria = get_object_or_404(CategoriaMateriaPrima, id=categoria_id, empresa=empresa)

        if materia_prima_id:  # Editar materia prima existente
            materia_prima = get_object_or_404(MateriaPrima, id=materia_prima_id, empresa=empresa)
            materia_prima.nombre = nombre
            materia_prima.descripcion = descripcion
            materia_prima.categoria = categoria
            materia_prima.cantidad = cantidad
            materia_prima.unidad_medida = unidad_medida
            materia_prima.precio_unitario = precio_unitario
            materia_prima.stock_minimo = stock_minimo
            materia_prima.save()
            messages.success(request, 'Materia prima actualizada exitosamente.')
        else:  # Crear nueva materia prima
            MateriaPrima.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                cantidad=cantidad,
                unidad_medida=unidad_medida,
                precio_unitario=precio_unitario,
                stock_minimo=stock_minimo,
                empresa=empresa
            )
            messages.success(request, 'Materia prima creada exitosamente.')

        return redirect('gestionar_materia_prima')

    return render(request, 'empresas/materia_prima/inventario.html', {
        'materias_primas': materias_primas,
        'categorias': categorias
    })

@login_required
@empresa_integral_required
def dashboard_materia_prima(request):
    empresa = request.user.microempresaintegral
    
    # Obtener estadísticas generales
    total_materias_primas = MateriaPrima.objects.filter(empresa=empresa).count()
    total_categorias = CategoriaMateriaPrima.objects.filter(empresa=empresa).count()
    
    # Calcular valor total del inventario
    materias_primas = MateriaPrima.objects.filter(empresa=empresa)
    valor_total_inventario = sum(mp.cantidad * mp.precio_unitario for mp in materias_primas)
    
    # Contar items con stock bajo
    stock_bajo = materias_primas.filter(cantidad__lte=F('stock_minimo')).count()
    
    # Obtener estadísticas por categoría
    categorias = CategoriaMateriaPrima.objects.filter(empresa=empresa).annotate(
        total_items=Count('materias_primas'),
        valor_total=Sum(F('materias_primas__cantidad') * F('materias_primas__precio_unitario'))
    )
    
    # Obtener últimos movimientos
    ultimos_movimientos = MovimientoMateriaPrima.objects.filter(
        materia_prima__empresa=empresa
    ).order_by('-fecha')[:5]
    
    # Obtener items con stock bajo para alertas
    alertas_stock = materias_primas.filter(cantidad__lte=F('stock_minimo'))

    # Movimientos por mes
    movimientos_mes = MovimientoMateriaPrima.objects.filter(
        materia_prima__empresa=empresa
    ).annotate(
        mes=TruncMonth('fecha')
    ).values('mes', 'tipo').annotate(
        total=Count('id')
    ).order_by('mes')
    
    # Top 5 materias primas más utilizadas
    top_materias = MovimientoMateriaPrima.objects.filter(
        materia_prima__empresa=empresa,
        tipo='salida'
    ).values(
        'materia_prima__nombre'
    ).annotate(
        total_usado=Sum('cantidad')
    ).order_by('-total_usado')[:5]

    return render(request, 'empresas/materia_prima/dashboard.html', {
        'total_materias_primas': total_materias_primas,
        'total_categorias': total_categorias,
        'valor_total_inventario': valor_total_inventario,
        'stock_bajo': stock_bajo,
        'categorias': categorias,
        'ultimos_movimientos': ultimos_movimientos,
        'alertas_stock': alertas_stock,
        'movimientos_mes': movimientos_mes,
        'top_materias': top_materias
    })

@login_required
@empresa_integral_required
def movimientos_materia_prima(request):
    empresa = request.user.microempresaintegral
    materias_primas = MateriaPrima.objects.filter(empresa=empresa)
    movimientos = MovimientoMateriaPrima.objects.filter(
        materia_prima__empresa=empresa
    ).order_by('-fecha')[:10]

    if request.method == 'POST':
        materia_prima_id = request.POST.get('materia_prima')
        tipo = request.POST.get('tipo')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')

        try:
            materia_prima = get_object_or_404(MateriaPrima, id=materia_prima_id, empresa=empresa)
            cantidad = int(cantidad)

            if cantidad <= 0:
                messages.error(request, 'La cantidad debe ser mayor que cero.')
                return redirect('movimientos_materia_prima')

            if tipo == 'salida' and cantidad > materia_prima.cantidad:
                messages.error(request, 'No hay suficiente stock disponible.')
                return redirect('movimientos_materia_prima')

            MovimientoMateriaPrima.objects.create(
                materia_prima=materia_prima,
                tipo=tipo,
                cantidad=cantidad,
                descripcion=descripcion
            )

            messages.success(request, f'Movimiento de {tipo} registrado exitosamente.')
            return redirect('movimientos_materia_prima')

        except ValueError:
            messages.error(request, 'Por favor ingrese una cantidad válida.')
        except Exception as e:
            messages.error(request, f'Error al registrar el movimiento: {str(e)}')

    return render(request, 'empresas/materia_prima/movimientos.html', {
        'materias_primas': materias_primas,
        'movimientos': movimientos
    })

@login_required
@empresa_integral_required
def eliminar_categoria_materia_prima(request, categoria_id):
    empresa = request.user.microempresaintegral
    categoria = get_object_or_404(CategoriaMateriaPrima, id=categoria_id, empresa=empresa)
    
    try:
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
    except Exception as e:
        messages.error(request, 'No se puede eliminar la categoría porque tiene materias primas asociadas.')
    
    return redirect('gestionar_categorias_materia_prima')

@login_required
@empresa_integral_required
def eliminar_materia_prima(request, materia_prima_id):
    empresa = request.user.microempresaintegral
    materia_prima = get_object_or_404(MateriaPrima, id=materia_prima_id, empresa=empresa)
    
    try:
        materia_prima.delete()
        messages.success(request, 'Materia prima eliminada exitosamente.')
    except Exception as e:
        messages.error(request, 'No se puede eliminar la materia prima porque tiene movimientos asociados.')
    
    return redirect('gestionar_materia_prima')