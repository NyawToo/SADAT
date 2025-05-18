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
    limpiarFiltros.className = 'btn btn-outline-secondary';
    limpiarFiltros.innerHTML = '<i class="fas fa-times"></i> Limpiar filtros';
    limpiarFiltros.onclick = function() {
        localStorage.removeItem('filtroEstado');
        localStorage.removeItem('filtroFecha');
        filtroEstado.value = '';
        filtroFecha.value = '';
        aplicarFiltros();
    };

    // Agregar botón de limpiar junto a los filtros
    const contenedorFiltros = document.querySelector('.d-flex.gap-2');
    contenedorFiltros.appendChild(limpiarFiltros);
}));