from django.shortcuts import render
from django.http import HttpResponseForbidden
import hashlib

class DevToolsProtectionMiddleware:
    """
    Middleware para proteger DevTools con contraseña
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Hash de la contraseña "andre792"
        self.password_hash = hashlib.sha256("andre792".encode()).hexdigest()

    def __call__(self, request):
        # Verificar si es una solicitud de DevTools
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Detectar Chrome DevTools
        if 'chrome-devtools' in user_agent or request.path.startswith('/.well-known/appspecific/'):
            # Verificar si ya está autenticado
            devtools_auth = request.session.get('devtools_authenticated', False)
            
            if not devtools_auth:
                # Verificar si se envió la contraseña
                password = request.GET.get('devtools_password') or request.POST.get('devtools_password')
                
                if password:
                    # Verificar contraseña
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    if password_hash == self.password_hash:
                        request.session['devtools_authenticated'] = True
                        request.session.set_expiry(3600)  # 1 hora
                    else:
                        return HttpResponseForbidden(
                            "<html><body><h1>Acceso Denegado</h1>"
                            "<p>Contraseña incorrecta para DevTools.</p>"
                            "</body></html>"
                        )
                else:
                    # Mostrar formulario de contraseña
                    return render(request, 'core/devtools_auth.html')
        
        response = self.get_response(request)
        return response
