// Sistema de notificaciones
let activeNotifications = new Set();

function showNotification(message, type = 'success') {
    // Si la notificación ya está activa, no la mostramos de nuevo
    if (activeNotifications.has(message)) {
        return;
    }

    // Agregar la notificación al conjunto de activas
    activeNotifications.add(message);

    // Crear el elemento de notificación
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'bottom: 200px; right: 20px; z-index: 1050; max-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Agregar la notificación al DOM
    document.body.appendChild(notification);

    // Configurar el temporizador para cerrar la notificación
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
            // Remover la notificación del conjunto de activas
            activeNotifications.delete(message);
        }, 100);
    }, 900);
}

// Función para mostrar notificaciones de éxito
function showSuccess(message) {
    showNotification(message, 'success');
}

// Función para mostrar notificaciones de error
function showError(message) {
    showNotification(message, 'danger');
}

// Función para mostrar notificaciones de advertencia
function showWarning(message) {
    showNotification(message, 'warning');
}

// Función para mostrar notificaciones informativas
function showInfo(message) {
    showNotification(message, 'info');
}