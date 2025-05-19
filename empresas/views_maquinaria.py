from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.decorators import role_required
from .models import Maquina, MicroempresaSatelite

@login_required
@role_required(['satelite'])
def gestionar_maquinaria(request):
    try:
        empresa = request.user.microempresasatelite
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            marca = request.POST.get('marca')
            modelo = request.POST.get('modelo')
            cantidad = request.POST.get('cantidad')
            descripcion = request.POST.get('descripcion')
            estado = request.POST.get('estado')
            imagen = request.FILES.get('imagen')

            if not all([nombre, tipo, marca, modelo, cantidad, estado]):
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('gestionar_maquinaria')

            try:
                cantidad = int(cantidad)
                if cantidad < 1:
                    raise ValueError
            except ValueError:
                messages.error(request, 'La cantidad debe ser un número entero positivo.')
                return redirect('gestionar_maquinaria')

            maquina = Maquina(
                empresa=empresa,
                nombre=nombre,
                tipo=tipo,
                marca=marca,
                modelo=modelo,
                cantidad=cantidad,
                descripcion=descripcion,
                estado=estado
            )
            if imagen:
                maquina.imagen = imagen
            maquina.save()
            messages.success(request, 'Máquina agregada exitosamente.')
            return redirect('gestionar_maquinaria')

        maquinaria = Maquina.objects.filter(empresa=empresa)
        return render(request, 'empresas/gestionar_maquinaria.html', {
            'maquinaria': maquinaria
        })
    except MicroempresaSatelite.DoesNotExist:
        messages.error(request, 'No se encontró la empresa satélite asociada a su usuario.')
        return redirect('home')

@login_required
@role_required(['satelite'])
def editar_maquina(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id, empresa=request.user.microempresasatelite)

    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            marca = request.POST.get('marca')
            modelo = request.POST.get('modelo')
            cantidad = request.POST.get('cantidad')
            descripcion = request.POST.get('descripcion')
            estado = request.POST.get('estado')
            imagen = request.FILES.get('imagen')

            if not all([nombre, tipo, marca, modelo, cantidad, estado]):
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('editar_maquina', maquina_id=maquina.id)

            try:
                cantidad = int(cantidad)
                if cantidad < 1:
                    raise ValueError
            except ValueError:
                messages.error(request, 'La cantidad debe ser un número entero positivo.')
                return redirect('editar_maquina', maquina_id=maquina.id)

            maquina.nombre = nombre
            maquina.tipo = tipo
            maquina.marca = marca
            maquina.modelo = modelo
            maquina.cantidad = cantidad
            maquina.descripcion = descripcion
            maquina.estado = estado
            if imagen:
                maquina.imagen = imagen
            maquina.save()

            messages.success(request, 'Máquina actualizada exitosamente.')
            return redirect('gestionar_maquinaria')
        except Exception as e:
            messages.error(request, f'Error al actualizar la máquina: {str(e)}')
            return redirect('editar_maquina', maquina_id=maquina.id)

    return render(request, 'empresas/editar_maquina.html', {
        'maquina': maquina
    })

@login_required
@role_required(['satelite'])
def eliminar_maquina(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id, empresa=request.user.microempresasatelite)
    try:
        maquina.delete()
        messages.success(request, 'Máquina eliminada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar la máquina: {str(e)}')
    return redirect('gestionar_maquinaria')