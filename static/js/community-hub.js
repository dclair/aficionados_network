// static/js/community-hub.js

const CommunityHub = {
    // 1. Previsualización de Imagen + Validación de Tamaño (ACTUALIZADO)
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
                    // --- NUEVA VALIDACIÓN DE TAMAÑO ---
                    if (file.size > MAX_SIZE_BYTES) {
                        alert(`¡Imagen demasiado pesada! El límite es de ${MAX_SIZE_MB}MB.`);
                        this.value = ""; // Vaciamos el input
                        placeholder.classList.remove('d-none');
                        preview.classList.add('d-none');
                        preview.innerHTML = "";
                        return;
                    }

                    // --- LÓGICA DE PREVISUALIZACIÓN ---
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        placeholder.classList.add('d-none');
                        // Mantenemos tu estilo de imagen, pero añadimos el id "image-preview" por si acaso
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

    // 2. Contador de Caracteres (MANTENIDO)
    initCharCounter: function() {
        const textarea = document.getElementById('id_caption');
        const counter = document.getElementById('charCounter');
        if (textarea && counter) {
            textarea.addEventListener('input', function() {
                counter.textContent = `${this.value.length} / 2000`;
            });
        }
    },

    // 3. Smart Scroll (Solo Móvil - MANTENIDO)
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

    // 4. Estado de Carga (Spinner - MANTENIDO)
    initLoadingState: function() {
        const form = document.getElementById('postForm');
        const btn = document.getElementById('submitBtn');
        if (form && btn) {
            form.addEventListener('submit', () => {
                btn.disabled = true;
                document.getElementById('btnText').classList.add('d-none');
                document.getElementById('btnSpinner').classList.remove('d-none');
            });
        }
    }
};

// Arrancar todas las funciones al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
    CommunityHub.initImagePreview();
    CommunityHub.initCharCounter();
    CommunityHub.initSmartScroll();
    CommunityHub.initLoadingState();
});