// Sistema de notificaciones
let activeNotifications = new Set();
let currentContext = '';
let contextStack = [];

// Función para establecer el contexto actual
function setNotificationContext(context) {
    if (context) {
        contextStack.push(context);
        currentContext = context;
    } else {
        if (contextStack.length > 0) {
            contextStack.pop();
            currentContext = contextStack.length > 0 ? contextStack[contextStack.length - 1] : '';
        } else {
            currentContext = '';
        }
    }
    // Limpiar notificaciones al cambiar de contexto
    activeNotifications.clear();
}

function showNotification(message, type = 'success', context = '') {
    // Validación más estricta del contexto
    if (context) {
        // Si hay un contexto específico, verificar si está en la pila de contextos
        if (!contextStack.includes(context)) {
            return;
        }
    } else if (currentContext) {
        // Si no se especifica contexto y hay uno activo, la notificación debe pertenecer al contexto actual
        return;
    }
    
    // Si la notificación ya está activa, no la mostramos de nuevo
    if (activeNotifications.has(message)) {
        return;
    }

    // Agregar la notificación al conjunto de activas
    activeNotifications.add(message);

    // Crear el elemento de notificación
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 300px;';
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
        }, 150);
    }, 2000);
}

// Función para mostrar notificaciones de éxito
function showSuccess(message, context = '') {
    showNotification(message, 'success', context);
}

// Función para mostrar notificaciones de error
function showError(message, context = '') {
    showNotification(message, 'danger', context);
}

// Función para mostrar notificaciones de advertencia
function showWarning(message, context = '') {
    showNotification(message, 'warning', context);
}

// Función para mostrar notificaciones informativas
function showInfo(message, context = '') {
    showNotification(message, 'info', context);
}