// static/js/community-hub.js

const CommunityHub = {
    // 1. Previsualización de Imagen
    initImagePreview: function() {
        const input = document.getElementById('id_image');
        const container = document.getElementById('imageUploadContainer');
        const preview = document.getElementById('imagePreview');
        const placeholder = document.getElementById('uploadPlaceholder');

        if (container && input) {
            container.addEventListener('click', () => input.click());
            input.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        placeholder.classList.add('d-none');
                        preview.innerHTML = `
                            <img src="${e.target.result}" class="img-fluid rounded shadow-sm mb-2" style="max-height: 200px;">
                            <p class="small text-danger mb-0" style="cursor:pointer;"><i class="bi bi-x-circle me-1"></i>Cambiar foto</p>
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

    // 4. Estado de Carga (Spinner)
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