function showModal(message, type, onConfirm) {
    let icon;
    switch(type) {
        case 'success': icon = 'success'; break;
        case 'error':   icon = 'error'; break;
        case 'alert':   icon = 'warning'; break;
        default:        icon = 'info';
    }

    Swal.fire({
        text: message,
        icon: icon,
        confirmButtonText: 'Aceptar',
        allowOutsideClick: false,
        allowEscapeKey: false,
        backdrop: true
    }).then(() => {
        if (typeof onConfirm === 'function') {
            onConfirm(); // ⬅️ AQUÍ está la “pausa”
        }
    });
}

