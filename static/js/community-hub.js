const CommunityHub = {
    // 1. Previsualización de Imagen + Validación de Tamaño
    initImagePreview: function() {
        const input = document.getElementById('id_image');
        const container = document.getElementById('imageUploadContainer');
        const preview = document.getElementById('imagePreview');
        const placeholder = document.getElementById('uploadPlaceholder');
        
        const MAX_SIZE_MB = 5;
        const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

        if (container && input) {
            container.addEventListener('click', () => input.click());
            
            input.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    if (file.size > MAX_SIZE_BYTES) {
                        alert(`¡Imagen demasiado pesada! El límite es de ${MAX_SIZE_MB}MB.`);
                        this.value = "";
                        placeholder.classList.remove('d-none');
                        preview.classList.add('d-none');
                        preview.innerHTML = "";
                        return;
                    }

                    const reader = new FileReader();
                    reader.onload = function(e) {
                        placeholder.classList.add('d-none');
                        preview.innerHTML = `
                            <img id="image-preview" src="${e.target.result}" class="img-fluid rounded shadow-sm mb-2" style="max-height: 250px; width: 100%; object-fit: cover;">
                            <p class="small text-danger mb-0" style="cursor:pointer;"><i class="bi bi-arrow-repeat me-1"></i>Cambiar foto</p>
                        `;
                        preview.classList.remove('d-none');
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    },

    // 2. Contador de Caracteres
    initCharCounter: function() {
        const textarea = document.getElementById('id_caption');
        const counter = document.getElementById('charCounter');
        if (textarea && counter) {
            textarea.addEventListener('input', function() {
                counter.textContent = `${this.value.length} / 2000`;
            });
        }
    },

    // 3. Smart Scroll (Solo Móvil)
    initSmartScroll: function() {
        const buttons = document.querySelectorAll('.btn-trending-view');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    const feed = document.querySelector('.col-lg-7');
                    if (feed) feed.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    },

    // 4. Estado de Carga (Spinner) - ¡ESTA ES LA VERSIÓN UNIFICADA!
    initLoadingState: function() {
        // Buscamos el botón con el ID exacto de tu HTML
        const submitBtn = document.getElementById('submit-btn');
        
        if (submitBtn) {
            // Buscamos el formulario al que pertenece el botón
            const form = submitBtn.closest('form');
            const spinner = document.getElementById('btn-spinner');
            const icon = document.getElementById('btn-icon');
            const text = document.getElementById('btn-text');

            if (form) {
                form.addEventListener('submit', function() {
                    // 1. Desactivar botón para evitar doble envío
                    submitBtn.disabled = true;
                    
                    // 2. Mostrar Spinner
                    if (spinner) spinner.classList.remove('d-none');
                    
                    // 3. Ocultar Icono
                    if (icon) icon.classList.add('d-none');
                    
                    // 4. Cambiar Texto
                    if (text) {
                        text.innerText = "Procesando...";
                    }
                });
            }
        }
    }
};

// Arrancar todas las funciones cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    CommunityHub.initImagePreview();
    CommunityHub.initCharCounter();
    CommunityHub.initSmartScroll();
    CommunityHub.initLoadingState(); // Se encarga de todo ahora
});


// Botón Back to Top
const mybutton = document.getElementById("btn-back-to-top");

window.onscroll = function () {
    if (document.documentElement.scrollTop > 50) {
        mybutton.classList.remove("d-none");
    } else {
        mybutton.classList.add("d-none");
    }
};

mybutton.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
});
   