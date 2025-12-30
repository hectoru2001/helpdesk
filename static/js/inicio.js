function actualizarHora() {
    const ahora = new Date();
    const hora = ahora.toLocaleTimeString('es-MX', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('hora-actual').textContent = hora;
}

actualizarHora();
setInterval(actualizarHora, 1000);
