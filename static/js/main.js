// Validación de formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Previsualización de imágenes
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;

    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Actualización dinámica de precios
function updateTotal(cantidad, precioUnitario, totalId) {
    const total = document.getElementById(totalId);
    if (!total) return;

    const monto = cantidad * precioUnitario;
    total.textContent = `$${monto.toFixed(2)}`;
}

// Inicialización de componentes Bootstrap
document.addEventListener('DOMContentLoaded', () => {
    // Establecer el contexto de la página actual
    const pageContext = document.body.dataset.pageContext || '';
    setNotificationContext(pageContext);

    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    // Las alertas ahora se manejan a través del sistema de notificaciones
    const alertList = document.querySelectorAll('.alert:not(.alert-cart)');
    alertList.forEach(alert => {
        const message = alert.textContent.trim();
        const type = alert.classList.contains('alert-success') ? 'success' :
                     alert.classList.contains('alert-danger') ? 'danger' :
                     alert.classList.contains('alert-warning') ? 'warning' : 'info';
        showNotification(message, type, pageContext);
        alert.remove();
    });
});

// Gestión de pedidos
function actualizarEstadoPedido(pedidoId, nuevoEstado) {
    fetch(`/pedidos/actualizar-estado/${pedidoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ estado: nuevoEstado })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const estadoBadge = document.querySelector(`#estado-pedido-${pedidoId}`);
            if (estadoBadge) {
                estadoBadge.textContent = nuevoEstado;
                estadoBadge.className = `estado-badge estado-${nuevoEstado.toLowerCase()}`;
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Función auxiliar para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Agregar al carrito
function agregarAlCarrito(productoId) {
    const cantidad = document.querySelector(`#cantidad-${productoId}`).value;
    
    fetch(`/pedidos/agregar-al-carrito/${productoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `cantidad=${cantidad}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar el stock mostrado
            const stockElement = document.querySelector(`#stock-${productoId}`);
            if (stockElement) {
                stockElement.textContent = data.nuevo_stock;
            }
            // Mostrar mensaje de éxito
            showSuccess('Producto agregado al carrito exitosamente', 'carrito');
        } else {
            showError(data.error || 'Error al agregar al carrito', 'carrito');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error al agregar al carrito', 'carrito');
    });
}

// Alternar la selección de checkboxes
function toggleCheckboxes() {
    const checkboxColumns = document.querySelectorAll('.checkbox-column');
    const toggleText = document.getElementById('toggle-text');
    const deleteButton = document.getElementById('delete-selected');
    const checkboxes = document.querySelectorAll('.item-checkbox');

    const isHidden = checkboxColumns[0].classList.contains('d-none');

    checkboxColumns.forEach(col => col.classList.toggle('d-none', !isHidden));
    deleteButton.classList.toggle('d-none', !isHidden);
    toggleText.textContent = isHidden ? 'Deseleccionar' : 'Seleccionar';

    if (isHidden) {
        checkboxes.forEach(cb => cb.checked = true); // Seleccionar todos
    } else {
        checkboxes.forEach(cb => cb.checked = false); // Deseleccionar todos
    }
}

// Eliminar del carrito
function eliminarDelCarrito() {
    const checkboxes = document.querySelectorAll('.item-checkbox:checked');
    const itemIds = Array.from(checkboxes).map(cb => cb.closest('tr').dataset.itemId);

    if (itemIds.length === 0) {
        showWarning('Por favor, selecciona al menos un producto para eliminar.', 'carrito');
        return;
    }

    if (confirm('¿Estás seguro de que deseas eliminar los productos seleccionados del carrito?')) {
        fetch('/pedidos/eliminar-del-carrito/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ item_ids: itemIds }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Eliminar las filas de la tabla
                itemIds.forEach(id => {
                    const row = document.querySelector(`tr[data-item-id="${id}"]`);
                    if (row) row.remove();
                });

                // Actualizar el resumen de la orden
                document.getElementById('subtotal').textContent = `$${parseFloat(data.subtotal).toFixed(2)}`;
                document.getElementById('iva').textContent = `$${parseFloat(data.iva).toFixed(2)}`;
                document.getElementById('total').textContent = `$${parseFloat(data.total).toFixed(2)}`;

                // Actualizar el contador de productos
                const itemCount = document.querySelectorAll('tr[data-item-id]').length;
                document.querySelector('.card-header h2').textContent = 
                    `Carro (${itemCount} producto${itemCount !== 1 ? 's' : ''})`;

                // Si el carrito está vacío, mostrar mensaje
                if (itemCount === 0) {
                    const table = document.querySelector('.table-responsive');
                    table.innerHTML = `
                        <div class="alert alert-info rounded-2" role="alert">
                            Tu carrito está vacío. <a href="/pedidos/lista_productos/" class="alert-link">¡Comienza a comprar!</a>
                        </div>`;
                    document.querySelector('.btn-primary.w-100').remove(); // Eliminar botón de continuar compra
                }

                alert(data.mensaje || 'Productos eliminados exitosamente.');
            } else {
                alert(data.error || 'Error al eliminar los productos.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ocurrió un error al procesar la solicitud.');
        });
    }
}