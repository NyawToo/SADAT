from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from empresas.models import ProductoTerminado

def detalle_producto(request, producto_id):
    producto = get_object_or_404(ProductoTerminado, id=producto_id)
    
    context = {
        'producto': producto
    }
    
    return render(request, 'pedidos/producto.html', context)