from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if this is an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                      request.headers.get('Content-Type') == 'application/json'
            
            if not request.user.is_authenticated:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Debe iniciar sesión para acceder a esta página'}, status=401)
                messages.error(request, 'Debe iniciar sesión para acceder a esta página')
                return redirect('login')
            
            if request.user.is_superuser:
                if 'superusuario' not in allowed_roles:
                    if is_ajax:
                        return JsonResponse({'success': False, 'error': 'No tiene permisos para acceder a esta página'}, status=403)
                    return redirect('reporte_global')
                return view_func(request, *args, **kwargs)
            
            if request.user.tipo not in allowed_roles:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'No tiene permisos para acceder a esta página'}, status=403)
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
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                  request.headers.get('Content-Type') == 'application/json'
        
        if not request.user.is_authenticated:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Debe iniciar sesión para acceder a esta página'}, status=401)
            messages.error(request, 'Debe iniciar sesión para acceder a esta página')
            return redirect('login')
        
        if request.user.tipo != 'integral':
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Solo las empresas integrales pueden acceder a esta página'}, status=403)
            messages.error(request, 'Solo las empresas integrales pueden acceder a esta página')
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return wrapper