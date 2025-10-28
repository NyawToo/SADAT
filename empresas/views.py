from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import MicroempresaIntegral, MicroempresaSatelite, ProductoTerminado, CategoriaProducto, Servicio
from .models_materia_prima import MateriaPrima
from core.decorators import role_required

@login_required
def catalogo_empresas(request):
    return render(request, 'empresas/catalogo_empresas.html')

@login_required
def catalogo_integrales(request):
    # Obtener búsqueda si existe
    search_query = request.GET.get('search', '')
    
    empresas = MicroempresaIntegral.objects.all()
    
    # Aplicar búsqueda si existe
    if search_query:
        empresas = empresas.filter(nombre_empresa__icontains=search_query)
    
    # Aplicar paginación
    paginator = Paginator(empresas, 12)  # 12 empresas por página
    page_number = request.GET.get('page', 1)
    empresas_paginadas = paginator.get_page(page_number)
    
    return render(request, 'empresas/catalogo_integrales.html', {
        'empresas': empresas_paginadas,
        'search_query': search_query
    })

@login_required
def catalogo_satelites(request):
    # Obtener búsqueda si existe
    search_query = request.GET.get('search', '')
    
    empresas = MicroempresaSatelite.objects.all()
    
    # Aplicar búsqueda si existe
    if search_query:
        empresas = empresas.filter(nombre_empresa__icontains=search_query)
    
    # Aplicar paginación
    paginator = Paginator(empresas, 12)  # 12 empresas por página
    page_number = request.GET.get('page', 1)
    empresas_paginadas = paginator.get_page(page_number)
    
    return render(request, 'empresas/catalogo_satelites.html', {
        'empresas': empresas_paginadas,
        'search_query': search_query
    })

@login_required
def detalle_empresa_integral(request, pk):
    empresa = get_object_or_404(MicroempresaIntegral, pk=pk)
    productos = ProductoTerminado.objects.filter(empresa=empresa)
    
    # Aplicar filtros si existen
    nombre = request.GET.get('nombre')
    categoria_id = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    if nombre:
        productos = productos.filter(nombre__icontains=nombre)
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if precio_min:
        productos = productos.filter(precio__gte=float(precio_min))
    if precio_max:
        productos = productos.filter(precio__lte=float(precio_max))
    
    pedidos_completados = 0  # Esto se actualizará cuando implementemos el sistema de pedidos
    calificacion_promedio = 0  # Esto se actualizará cuando implementemos el sistema de calificaciones
    
    # Obtener datos de contacto del usuario asociado
    direccion = empresa.usuario.direccion
    telefono = empresa.usuario.telefono
    email = empresa.usuario.email
    
    # Obtener todas las categorías para el filtro
    from empresas.models import CategoriaProducto
    categorias = CategoriaProducto.objects.all()
    
    return render(request, 'empresas/detalle_empresa_integral.html', {
        'empresa': empresa,
        'productos': productos,
        'pedidos_completados': pedidos_completados,
        'calificacion_promedio': calificacion_promedio,
        'direccion': direccion,
        'telefono': telefono,
        'email': email,
        'categorias': categorias,
        # Devolver los valores actuales de los filtros
        'nombre_filtro': nombre,
        'categoria_filtro': categoria_id,
        'precio_min_filtro': precio_min,
        'precio_max_filtro': precio_max
    })

@login_required
def detalle_empresa_satelite(request, pk):
    empresa = get_object_or_404(MicroempresaSatelite, pk=pk)
    servicios = Servicio.objects.filter(empresa=empresa)
    maquinaria = empresa.maquinaria.all()
    puede_solicitar = request.user.tipo == 'cliente'
    
    # Obtener datos de contacto del usuario asociado si no están especificados en la empresa
    direccion = empresa.direccion or empresa.usuario.direccion
    telefono = empresa.telefono or empresa.usuario.telefono
    email = empresa.email or empresa.usuario.email
    
    return render(request, 'empresas/detalle_empresa_satelite.html', {
        'empresa': empresa,
        'servicios': servicios,
        'maquinaria': maquinaria,
        'puede_solicitar': puede_solicitar,
        'solicitar_confeccion_url': 'solicitar_confeccion',
        'direccion': direccion,
        'telefono': telefono,
        'email': email
    })

@login_required
def gestionar_materia_prima(request):
    materias_primas = MateriaPrima.objects.all()
    return render(request, 'empresas/gestionar_materia_prima.html', {
        'materias_primas': materias_primas
    })

@login_required
def gestionar_productos(request):
    if request.user.tipo != 'integral':
        messages.error(request, 'Solo las empresas integrales pueden gestionar productos')
        return redirect('home')
    
    try:
        empresa = request.user.microempresaintegral
        productos = ProductoTerminado.objects.filter(empresa=empresa)
        categorias = CategoriaProducto.objects.all()
        if not categorias.exists():
            messages.warning(request, 'No hay categorías disponibles. Por favor, cree una categoría primero.')
        return render(request, 'empresas/gestionar_productos.html', {
            'productos': productos,
            'categorias': categorias,
            'editing': False
        })
    except Exception as e:
        messages.error(request, 'Error al cargar los productos')
        return redirect('home')

@login_required
@role_required(['satelite'])
def agregar_servicios(request):
    if request.method == 'POST':
        try:
            empresa = request.user.microempresasatelite
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio_minimo = request.POST.get('precio_minimo')
            precio_maximo = request.POST.get('precio_maximo')

            if not all([nombre, descripcion, precio_minimo, precio_maximo]):
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('agregar_servicios')

            try:
                precio_minimo = float(precio_minimo)
                precio_maximo = float(precio_maximo)
                if precio_minimo < 0 or precio_maximo < 0:
                    raise ValueError
                if precio_minimo > precio_maximo:
                    messages.error(request, 'El precio mínimo no puede ser mayor que el precio máximo.')
                    return redirect('agregar_servicios')
            except ValueError:
                messages.error(request, 'Los precios deben ser valores numéricos válidos y positivos.')
                return redirect('agregar_servicios')

            Servicio.objects.create(
                empresa=empresa,
                nombre=nombre,
                descripcion=descripcion,
                precio_minimo=precio_minimo,
                precio_maximo=precio_maximo
            )
            messages.success(request, 'Servicio agregado exitosamente.')
            return redirect('agregar_servicios')
        except Exception as e:
            messages.error(request, f'Error al crear el servicio: {str(e)}')
            return redirect('agregar_servicios')

    servicios = Servicio.objects.filter(empresa=request.user.microempresasatelite).order_by('-fecha_creacion')
    return render(request, 'empresas/agregar_servicios.html', {
        'servicios': servicios
    })