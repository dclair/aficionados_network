// static/js/forms.js

(function () {
  'use strict'

  document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        // Si el formulario es válido, activamos el efecto de carga
        if (form.checkValidity()) {
          const btn = form.querySelector('button[type="submit"]');
          const spinner = btn.querySelector('.spinner-border');
          const btnText = btn.querySelector('span:last-child');

          if (btn) {
            // Deshabilitamos el botón para evitar múltiples clics
            btn.disabled = true;
            // Mostramos el spinner quitando la clase 'd-none' de Bootstrap
            if (spinner) spinner.classList.remove('d-none');
            // Cambiamos el texto para dar feedback visual
            if (btnText) btnText.textContent = ' Procesando...';
          }
        } else {
          event.preventDefault();
          event.stopPropagation();
        }

        form.classList.add('was-validated');
      }, false);
    });
  });
})();