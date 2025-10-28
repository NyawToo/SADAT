// Validación de formularios con mejor feedback visual
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
            field.style.borderColor = '#ef4444';
            field.style.animation = 'shake 0.3s ease';
        } else {
            field.classList.remove('is-invalid');
            field.style.borderColor = '#10b981';
        }
    });

    return isValid;
}

// Animación de shake para campos inválidos
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
`;
document.head.appendChild(style);

// Previsualización de imágenes con animación
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;

    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.style.opacity = '0';
            setTimeout(() => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                preview.style.opacity = '1';
                preview.style.transition = 'opacity 0.3s ease';
            }, 100);
        };
        reader.readAsDataURL(file);
    }
}

// Actualización dinámica de precios con animación
function updateTotal(cantidad, precioUnitario, totalId) {
    const total = document.getElementById(totalId);
    if (!total) return;

    const monto = cantidad * precioUnitario;
    
    // Animación de actualización
    total.style.transform = 'scale(1.1)';
    total.style.color = '#60a5fa';
    
    setTimeout(() => {
        total.textContent = `$${monto.toFixed(2)}`;
        total.style.transform = 'scale(1)';
        total.style.color = '';
    }, 150);
}

// Inicialización de componentes Bootstrap
document.addEventListener('DOMContentLoaded', () => {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    // Alertas automáticas (excepto las del carrito y las auto-dismiss)
    const alertList = document.querySelectorAll('.alert:not(.alert-cart):not(.auto-dismiss-alert)');
    alertList.forEach(alert => {
        if (alert) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 900); // 1.5 segundos
        }
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
            alert('Producto agregado al carrito exitosamente');
        } else {
            alert(data.error || 'Error al agregar al carrito');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al agregar al carrito');
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
        alert('Por favor, selecciona al menos un producto para eliminar.');
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