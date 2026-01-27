// static/js/cookies.js

document.addEventListener("DOMContentLoaded", function() {
    const cookieBanner = document.getElementById('cookie-banner');
    const acceptBtn = document.getElementById('accept-cookies');

    // 1. Verificamos si ya existe la decisión en el navegador
    if (cookieBanner && !localStorage.getItem('cookies-accepted')) {
        cookieBanner.style.display = 'block';
    }

    // 2. Lógica del botón de aceptar
    if (acceptBtn) {
        acceptBtn.addEventListener('click', function() {
            localStorage.setItem('cookies-accepted', 'true');
            
            // Efecto de salida suave
            cookieBanner.style.transition = "opacity 0.5s ease";
            cookieBanner.style.opacity = "0";
            
            setTimeout(() => {
                cookieBanner.style.display = 'none';
            }, 500);
        });
    }
});