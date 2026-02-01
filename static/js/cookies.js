document.addEventListener("DOMContentLoaded", function() {
    const banner = document.getElementById('cookie-banner');
    const acceptBtn = document.getElementById('accept-cookies');
    const rejectBtn = document.getElementById('reject-cookies'); // <--- Añadimos esta referencia

    // 1. Verificar si ya se tomó una decisión previa
    if (localStorage.getItem('hubs-cookies-accepted')) {
        banner.style.display = 'none';
    }

    // 2. Lógica para ACEPTAR TODO
    if (acceptBtn) {
        acceptBtn.addEventListener('click', () => {
            localStorage.setItem('hubs-cookies-accepted', 'all');
            banner.classList.add('hidden'); // Activa la animación de bajada del CSS
        });
    }

    // 3. Lógica para RECHAZAR / SOLO NECESARIAS
    if (rejectBtn) {
        rejectBtn.addEventListener('click', () => {
            localStorage.setItem('hubs-cookies-accepted', 'essential');
            banner.classList.add('hidden'); // También lo ocultamos
        });
    }
});