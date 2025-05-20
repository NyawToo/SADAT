document.addEventListener('DOMContentLoaded', function() {
    const filtroEstado = document.getElementById('filtroEstado');
    const filtroFecha = document.getElementById('filtroFecha');
    const solicitudesRows = document.querySelectorAll('tbody tr');

    // Cargar valores guardados
    const estadoGuardado = localStorage.getItem('filtroEstado');
    const fechaGuardada = localStorage.getItem('filtroFecha');

    if (estadoGuardado) {
        filtroEstado.value = estadoGuardado;
    }
    if (fechaGuardada) {
        filtroFecha.value = fechaGuardada;
    }

    function aplicarFiltros() {
        const estado = filtroEstado.value;
        const fecha = filtroFecha.value;

        // Guardar valores en localStorage
        localStorage.setItem('filtroEstado', estado);
        localStorage.setItem('filtroFecha', fecha);

        solicitudesRows.forEach(row => {
            let mostrar = true;
            const estadoSolicitud = row.querySelector('td:nth-child(6) .badge').textContent.toLowerCase();
            const fechaSolicitud = row.querySelector('td:nth-child(5)').textContent;

            if (estado && estadoSolicitud !== estado.toLowerCase()) {
                mostrar = false;
            }

            if (fecha && fechaSolicitud !== fecha) {
                mostrar = false;
            }

            row.style.display = mostrar ? '' : 'none';
        });
    }

    // Aplicar filtros al cargar la página
    aplicarFiltros();

    // Eventos para actualizar filtros
    filtroEstado.addEventListener('change', aplicarFiltros);
    filtroFecha.addEventListener('change', aplicarFiltros);

    // Botón para limpiar filtros
    const limpiarFiltros = document.createElement('button');
    limpiarFiltros.className = 'btn btn-outline-secondary ms-2';
    limpiarFiltros.innerHTML = '<i class="fas fa-times"></i> Limpiar filtros';
    limpiarFiltros.onclick = function() {
        localStorage.removeItem('filtroEstado');
        localStorage.removeItem('filtroFecha');
        filtroEstado.value = '';
        filtroFecha.value = '';
        aplicarFiltros();
    };

    // Agregar botón de limpiar junto a los filtros
    const contenedorFiltros = document.querySelector('.card-header .d-flex.gap-2');
    if (contenedorFiltros) {
        contenedorFiltros.appendChild(limpiarFiltros);
    }
});

function enviarCotizacion(solicitudId) {
    const precio = document.getElementById(`precio${solicitudId}`).value;
    const tiempo = document.getElementById(`tiempo${solicitudId}`).value;
    const comentarios = document.getElementById(`comentarios${solicitudId}`).value;

    if (!precio || !tiempo) {
        alert('Por favor, complete todos los campos requeridos');
        return;
    }

    // Obtener el token CSRF del elemento meta en el HTML
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/pedidos/confeccion/cotizar/${solicitudId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            precio_por_prenda: parseFloat(precio),
            tiempo_estimado: parseInt(tiempo),
            comentarios: comentarios
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.error || 'Error al enviar la cotización');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la solicitud');
    });
}