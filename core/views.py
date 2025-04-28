from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Usuario
from .forms import CustomUserCreationForm
from .forms_empresa import ClienteRegistrationForm, EmpresaIntegralRegistrationForm, EmpresaSateliteRegistrationForm
from empresas.models import MicroempresaIntegral, MicroempresaSatelite

def inicio(request):
    if request.user.is_authenticated:
        if request.user.tipo == 'integral':
            return redirect('gestionar_productos') # Redirigir a gestionar_productos
        elif request.user.tipo == 'satelite':
            return redirect('gestionar_solicitudes_confeccion')
        elif request.user.tipo == 'cliente':
            return redirect('catalogo_empresas')
        elif request.user.tipo == 'superusuario':
            return redirect('reporte_global')
        else:
            return redirect('home')
    return render(request, 'core/inicio.html')


def registro_cliente(request):
    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión con tus credenciales.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ClienteRegistrationForm()
    return render(request, 'core/registro_cliente.html', {'form': form})

def registro_integral(request):
    if request.method == 'POST':
        form = EmpresaIntegralRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión con tus credenciales.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = EmpresaIntegralRegistrationForm()
    return render(request, 'core/registro_integral.html', {'form': form})

def registro_satelite(request):
    if request.method == 'POST':
        form = EmpresaSateliteRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión con tus credenciales.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = EmpresaSateliteRegistrationForm()
    return render(request, 'core/registro_satelite.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Por favor ingrese usuario y contraseña')
            return render(request, 'core/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso')
                
                if user.is_superuser or user.tipo == 'superusuario':
                    return redirect('reporte_global')
                elif user.tipo == 'integral':
                    return redirect('gestionar_productos') # Redirigir a gestionar_productos
                elif user.tipo == 'satelite':
                    return redirect('gestionar_solicitudes_confeccion')
                elif user.tipo == 'cliente':
                    return redirect('catalogo_empresas')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Usuario inactivo')
                return render(request, 'core/login.html')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'core/login.html')
    else:
        return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    messages.get_messages(request).used = True  # Limpia los mensajes anteriores
    messages.info(request, 'Has cerrado sesión')
    return redirect('login')

@login_required
def perfil(request):
    messages.get_messages(request).used = True  # Limpia los mensajes anteriores
    if request.method == 'POST':
        # Actualizar datos del perfil
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.telefono = request.POST.get('telefono', user.telefono)
        user.direccion = request.POST.get('direccion', user.direccion)
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente')
        
    return render(request, 'core/perfil.html')

@login_required
def crear_superadmin(request):
    if not request.user.is_superuser and request.user.tipo != 'superusuario':
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_superuser = True
            usuario.tipo = 'superusuario'
            usuario.save()
            messages.success(request, f'Superadministrador {usuario.username} creado exitosamente')
            return redirect('gestionar_usuarios')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/crear_superadmin.html', {'form': form})

@login_required
def editar_usuario(request, usuario_id):
    if not request.user.is_superuser and request.user.tipo != 'superusuario':
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('home')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        if request.method == 'POST':
            usuario.email = request.POST.get('email')
            usuario.telefono = request.POST.get('telefono')
            usuario.direccion = request.POST.get('direccion')
            usuario.save()
            messages.success(request, f'Usuario {usuario.username} actualizado exitosamente')
            return redirect('gestionar_usuarios')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('gestionar_usuarios')

@login_required
def gestionar_usuarios(request):
    if not request.user.is_superuser and request.user.tipo != 'superusuario':
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('home')
        
    # Obtener usuarios por tipo
    clientes = Usuario.objects.filter(tipo='cliente')
    empresas_integrales = MicroempresaIntegral.objects.all()
    empresas_satelites = MicroempresaSatelite.objects.all()
    
    context = {
        'clientes': clientes,
        'empresas_integrales': empresas_integrales,
        'empresas_satelites': empresas_satelites,
    }
    
    return render(request, 'core/gestionar_usuarios.html', context)
    
    # Obtener usuarios por tipo
    clientes = Usuario.objects.filter(tipo='cliente')
    empresas_integrales = MicroempresaIntegral.objects.all()
    empresas_satelites = MicroempresaSatelite.objects.all()
    
    context = {
        'clientes': clientes,
        'empresas_integrales': empresas_integrales,
        'empresas_satelites': empresas_satelites,
    }
    
    return render(request, 'core/gestionar_usuarios.html', context)
    
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        action = request.POST.get('action')
        
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            if action == 'activar':
                usuario.is_active = True
                messages.success(request, f'Usuario {usuario.username} activado exitosamente')
            elif action == 'desactivar':
                usuario.is_active = False
                messages.success(request, f'Usuario {usuario.username} desactivado exitosamente')
            usuario.save()
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')

@login_required
def eliminar_usuario(request, usuario_id):
    if not request.user.is_superuser and request.user.tipo != 'superusuario':
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('home')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario {username} eliminado exitosamente')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
    
    return redirect('gestionar_usuarios')
    
    # Filtrar usuarios por tipo
    clientes = Usuario.objects.filter(tipo='cliente').order_by('username')
    empresas_integrales = Usuario.objects.filter(tipo='integral').order_by('username')
    empresas_satelites = Usuario.objects.filter(tipo='satelite').order_by('username')
    
    context = {
        'clientes': clientes,
        'empresas_integrales': empresas_integrales,
        'empresas_satelites': empresas_satelites
    }
    
    return render(request, 'core/gestionar_usuarios.html', context)