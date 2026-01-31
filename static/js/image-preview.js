// static/js/image-preview.js
document.addEventListener('change', function(e) {
    // Verificamos si el cambio viene de un input de imagen
    if (e.target.matches('input[type="file"]')) {
        const input = e.target;
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                // Buscamos los elementos de feedback en la misma tarjeta
                const container = input.closest('.post-update-file-container');
                const previewImg = container.querySelector('#image-preview');
                const previewContainer = container.querySelector('#preview-container');
                const statusText = container.querySelector('#file-status');
                const icon = container.querySelector('#upload-icon');

                if (previewImg) {
                    previewImg.src = e.target.result;
                    previewContainer.classList.remove('d-none');
                    if (icon) icon.classList.add('d-none');
                    if (statusText) statusText.innerText = "¡Imagen seleccionada!";
                }
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
});