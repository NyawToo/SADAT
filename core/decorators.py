from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debe iniciar sesión para acceder a esta página')
                return redirect('login')
            
            if request.user.is_superuser:
                return redirect('reporte_global') if 'superusuario' not in allowed_roles else view_func(request, *args, **kwargs)
            
            if request.user.tipo not in allowed_roles:
                messages.error(request, 'No tiene permisos para acceder a esta página')
                if request.user.tipo == 'integral':
                    return redirect('gestionar_pedidos')
                elif request.user.tipo == 'satelite':
                    return redirect('gestionar_solicitudes_confeccion')
                elif request.user.tipo == 'cliente':
                    return redirect('catalogo_empresas')
                elif request.user.tipo == 'superusuario':
                    return redirect('reporte_global')
                else:
                    return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def empresa_integral_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesión para acceder a esta página')
            return redirect('login')
        
        if request.user.tipo != 'integral':
            messages.error(request, 'Solo las empresas integrales pueden acceder a esta página')
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return wrapper