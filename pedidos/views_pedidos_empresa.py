from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from core.decorators import empresa_integral_required
from .models import Pedido

@login_required
@empresa_integral_required
def lista_pedidos_empresa(request):
    empresa = request.user.microempresaintegral
    pedidos = Pedido.objects.filter(empresa=empresa).order_by('-fecha_pedido')
    return render(request, 'pedidos/lista_pedidos_empresa.html', {'pedidos': pedidos})

@login_required
@empresa_integral_required
def actualizar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, empresa=request.user.microempresaintegral)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        # Use states defined in the model for validation
        estados_validos = [estado[0] for estado in Pedido.ESTADOS]
        
        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
            pedido.save()
            
            # Crear notificación para el cliente
            from notificaciones.models import Notificacion
            Notificacion.objects.create(
                usuario=pedido.cliente,
                tipo='pedido_actualizado',
                titulo='Actualización de pedido',
                mensaje=f'Tu pedido #{pedido.id} ha sido actualizado a estado: {pedido.get_estado_display()}', # Use get_estado_display for user-friendly name
                prioridad='alta'
            )
            
            messages.success(request, 'Estado del pedido actualizado correctamente')
        else:
            messages.error(request, 'Estado no válido')
    
    # Redirect to the main management view for consistency
    return redirect('gestionar_pedidos')