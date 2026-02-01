/**
 * image_validator.js
 * Gestiona validación de tamaño, formato y previsualización de imágenes.
 */
document.addEventListener("DOMContentLoaded", function() {
    const MAX_SIZE_MB = 5;
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

    const imageInput = document.querySelector('.validate-image');
    const previewImg = document.getElementById('image-preview');
    const previewContainer = document.getElementById('imagePreview');
    const placeholder = document.getElementById('uploadPlaceholder');

    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];

            if (file) {
                // 1. Validar Peso
                if (file.size > MAX_SIZE_BYTES) {
                    alert(`¡Imagen demasiado pesada! El límite es de ${MAX_SIZE_MB}MB.`);
                    this.value = ""; // Limpiamos el input
                    
                    // Si hay error, volvemos al estado inicial de la UI
                    if (previewContainer) previewContainer.classList.add('d-none');
                    if (placeholder) placeholder.classList.remove('d-none');
                    return;
                }

                // 2. Procesar Previsualización
                if (previewImg) {
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        previewImg.src = e.target.result;
                        
                        // Intercambio de visibilidad en la interfaz
                        if (placeholder) placeholder.classList.add('d-none');
                        if (previewContainer) previewContainer.classList.remove('d-none');
                    }
                    
                    reader.readAsDataURL(file);
                }
            } else {
                // Si el usuario cancela la selección, volvemos al placeholder
                if (previewContainer) previewContainer.classList.add('d-none');
                if (placeholder) placeholder.classList.remove('d-none');
            }
        });
    }
});