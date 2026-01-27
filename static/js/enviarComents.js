// static/js/ui.js

document.addEventListener('DOMContentLoaded', function() {
    // Buscamos el formulario de comentarios
    const commentForm = document.querySelector('form[action*="comment"]');
    
    if (commentForm) {
        commentForm.addEventListener('submit', function() {
            const btn = document.getElementById('btn-submit-comment');
            const spinner = document.getElementById('spinner-comment');
            const btnText = document.getElementById('btn-text-comment');

            if (btn) {
                // 1. Desactivamos el botón para evitar múltiples clics
                btn.disabled = true;
                
                // 2. Mostramos el spinner quitando la clase d-none de Bootstrap
                if (spinner) spinner.classList.remove('d-none');
                
                // 3. Cambiamos el texto para dar feedback
                if (btnText) btnText.innerText = 'Enviando...';
            }
        });
    }
});