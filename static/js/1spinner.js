/**
 * Spinner Handler para formularios de Community Hub
 * Activa la animación de carga y deshabilita el botón al enviar.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Buscamos todos los formularios con la clase 'js-form-loading'
    const loadingForms = document.querySelectorAll('.js-form-loading');

    loadingForms.forEach(form => {
        form.addEventListener('submit', function() {
            const btn = this.querySelector('button[type="submit"]');
            
            if (btn) {
                const spinner = btn.querySelector('.btn-spinner');
                const text = btn.querySelector('.btn-text');

                // 1. Deshabilitar botón (evita envíos duplicados)
                btn.disabled = true;

                // 2. Mostrar spinner (quitando d-none de Bootstrap)
                if (spinner) {
                    spinner.classList.remove('d-none');
                }

                // 3. Efecto visual opcional en el texto
                if (text) {
                    text.style.opacity = '0.7';
                }
            }
        });
    });
});