from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import ProductoTerminado, ComentarioProducto, CalificacionProducto, CategoriaProducto, MicroempresaIntegral

@login_required
def gestionar_categorias(request):
    if request.user.tipo != 'integral':
        messages.error(request, 'Solo las empresas integrales pueden gestionar categorías')
        return redirect('home')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')

        if not nombre:
            messages.error(request, 'El nombre de la categoría es obligatorio.')
            return redirect('gestionar_categorias')

        try:
            CategoriaProducto.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('gestionar_categorias')
        except Exception as e:
            messages.error(request, f'Error al crear la categoría: {str(e)}')

    categorias = CategoriaProducto.objects.all()
    return render(request, 'empresas/gestionar_categorias.html', {
        'categorias': categorias
    })

@login_required
def eliminar_categoria(request, categoria_id):
    if request.user.tipo != 'integral':
        messages.error(request, 'Solo las empresas integrales pueden eliminar categorías')
        return redirect('home')

    if request.method == 'POST':
        categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
        try:
            categoria.delete()
            messages.success(request, 'Categoría eliminada exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar la categoría: {str(e)}')

    return redirect('gestionar_categorias')

@login_required
def agregar_comentario(request, producto_id):
    if request.method == 'POST' and request.user.tipo == 'cliente':
        producto = get_object_or_404(ProductoTerminado, id=producto_id)
        texto = request.POST.get('texto')
        
        if texto:
            comentario = ComentarioProducto.objects.create(
                producto=producto,
                usuario=request.user,
                texto=texto
            )
            return JsonResponse({'success': True})
        
    return JsonResponse({'success': False, 'error': 'No se pudo agregar el comentario'})

@login_required
def calificar_producto(request, producto_id):
    if request.method == 'POST' and request.user.tipo == 'cliente':
        producto = get_object_or_404(ProductoTerminado, id=producto_id)
        puntuacion = request.POST.get('puntuacion')
        
        try:
            puntuacion = int(puntuacion)
            if 1 <= puntuacion <= 5:
                CalificacionProducto.objects.update_or_create(
                    producto=producto,
                    usuario=request.user,
                    defaults={'puntuacion': puntuacion}
                )
                
                # Actualizar calificación promedio
                promedio = producto.calificaciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
                return JsonResponse({'success': True, 'promedio': round(promedio, 1)})
        except (ValueError, TypeError):
            pass
            
    return JsonResponse({'success': False, 'error': 'No se pudo calificar el producto'})

@login_required
def dar_like(request, comentario_id):
    if request.method == 'POST' and request.user.tipo == 'cliente':
        comentario = get_object_or_404(ComentarioProducto, id=comentario_id)
        comentario.likes += 1
        comentario.save()
        return JsonResponse({'success': True, 'likes': comentario.likes})
    return JsonResponse({'success': False})

@login_required
def dar_dislike(request, comentario_id):
    if request.method == 'POST' and request.user.tipo == 'cliente':
        comentario = get_object_or_404(ComentarioProducto, id=comentario_id)
        comentario.dislikes += 1
        comentario.save()
        return JsonResponse({'success': True, 'dislikes': comentario.dislikes})
    return JsonResponse({'success': False})

@login_required
def crear_producto(request):
    if request.user.tipo != 'integral':
        messages.error(request, 'Solo las empresas integrales pueden crear productos')
        return redirect('home')

    try:
        empresa_integral = request.user.microempresaintegral
    except MicroempresaIntegral.DoesNotExist:
        messages.error(request, 'No se encontró la empresa integral asociada')
        return redirect('gestionar_productos')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        imagen = request.FILES.get('imagen')
        categoria_id = request.POST.get('categoria')

        # Validar campos requeridos
        if not all([nombre, precio, stock, categoria_id]):
            messages.error(request, 'Por favor, complete todos los campos requeridos.')
            return redirect('gestionar_productos')

        try:
            precio = float(precio)
            stock = int(stock)
            if precio <= 0:
                messages.error(request, 'El precio debe ser mayor que cero.')
                return redirect('gestionar_productos')
            if stock < 0:
                messages.error(request, 'El stock no puede ser negativo.')
                return redirect('gestionar_productos')

            # Validar categoría
            categoria = get_object_or_404(CategoriaProducto, id=categoria_id)

            # Crear el producto
            producto = ProductoTerminado(
                empresa=empresa_integral,
                nombre=nombre,
                descripcion=descripcion or '',
                precio=precio,
                stock=stock,
                imagen=imagen,
                categoria=categoria
            )
            producto.full_clean()  # Ejecuta validaciones del modelo
            producto.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('gestionar_productos')

        except ValueError:
            messages.error(request, 'El precio y el stock deben ser valores numéricos válidos.')
        except ValidationError as e:
            messages.error(request, f'Error en los datos del producto: {str(e)}')
        except IntegrityError:
            messages.error(request, 'Ya existe un producto con ese nombre para esta empresa.')
        except Exception as e:
            messages.error(request, f'Error inesperado al crear el producto: {str(e)}')

    # Si no es POST, renderizar el formulario
    productos = ProductoTerminado.objects.filter(empresa=empresa_integral)
    categorias = CategoriaProducto.objects.all()
    return render(request, 'empresas/gestionar_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'editing': False
    })

@login_required
def editar_producto(request, producto_id):
    if request.user.tipo != 'integral':
        messages.error(request, 'Solo las empresas integrales pueden editar productos')
        return redirect('home')

    producto = get_object_or_404(ProductoTerminado, id=producto_id, empresa=request.user.microempresaintegral)
    categorias = CategoriaProducto.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        categoria_id = request.POST.get('categoria')
        imagen = request.FILES.get('imagen')

        if not all([nombre, precio, stock, categoria_id]):
            messages.error(request, 'Por favor, complete todos los campos requeridos.')
            return redirect('gestionar_productos')

        try:
            producto.nombre = nombre
            producto.descripcion = descripcion or ''
            producto.categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
            precio_float = float(precio)
            stock_int = int(stock)

            if precio_float <= 0:
                messages.error(request, 'El precio debe ser mayor que cero.')
                return redirect('gestionar_productos')
            if stock_int < 0:
                messages.error(request, 'El stock no puede ser negativo.')
                return redirect('gestionar_productos')

            producto.precio = precio_float
            producto.stock = stock_int

            if imagen:
                producto.imagen = imagen

            producto.full_clean()  # Ejecuta validaciones del modelo
            producto.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('gestionar_productos')

        except ValueError:
            messages.error(request, 'El precio y el stock deben ser valores numéricos válidos.')
        except ValidationError as e:
            messages.error(request, f'Error en los datos del producto: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error inesperado al actualizar el producto: {str(e)}')

    return render(request, 'empresas/editar_producto.html', {
        'producto': producto,
        'categorias': categorias
    })

@login_required
def eliminar_producto(request, producto_id):
    if request.method == 'POST' and request.user.tipo == 'integral':
        producto = get_object_or_404(ProductoTerminado, id=producto_id, empresa=request.user.microempresaintegral)
        try:
            producto.delete()
            messages.success(request, 'Producto eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar el producto: {str(e)}')
    return redirect('gestionar_productos')