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

    // 4. Estado de Carga (Spinner) - ¡VERSION MEJORADA Y UNIVERSAL!
    initLoadingState: function() {
        /**
         * Esta función ahora escucha CUALQUIER formulario con la clase .js-form-loading
         * o el botón específico #submit-btn.
         */
        document.addEventListener('submit', function(e) {
            const form = e.target;
            
            // Caso A: Formularios de la lista de eventos (.js-form-loading)
            if (form.classList.contains('js-form-loading')) {
                const button = form.querySelector('button[type="submit"]');
                if (button) {
                    const spinner = button.querySelector('.btn-spinner');
                    const text = button.querySelector('.btn-text');
                    
                    if (spinner) spinner.classList.remove('d-none');
                    if (text) text.classList.add('d-none');
                    
                    button.disabled = true;
                    button.classList.add('disabled');
                }
            }
            
            // Caso B: El botón único de "Crear Post" (#submit-btn)
            const submitBtn = document.getElementById('submit-btn');
            if (submitBtn && form.contains(submitBtn)) {
                const spinner = document.getElementById('btn-spinner');
                const icon = document.getElementById('btn-icon');
                const text = document.getElementById('btn-text');

                submitBtn.disabled = true;
                if (spinner) spinner.classList.remove('d-none');
                if (icon) icon.classList.add('d-none');
                if (text) text.innerText = "Procesando...";
            }
        });
    }
};

// --- RESTO DEL CODIGO (Masonry, Back to Top, Validation) SE MANTIENE IGUAL ---
document.addEventListener('DOMContentLoaded', () => {
    CommunityHub.initImagePreview();
    CommunityHub.initCharCounter();
    CommunityHub.initSmartScroll();
    CommunityHub.initLoadingState();
});

// Botón Back to Top
const mybutton = document.getElementById("btn-back-to-top");
if (mybutton) {
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
}

// Validación de Bootstrap
(function () {
    'use strict'
    document.addEventListener('DOMContentLoaded', function() {
        const forms = document.querySelectorAll('.needs-validation');
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    });
})();

// Masonry y HTMX
(function() {
    'use strict';
    document.addEventListener('DOMContentLoaded', function() {
        const gridContainer = document.querySelector('.clicks-grid');
        let msnry;

        if (gridContainer) {
            imagesLoaded(gridContainer, function() {
                msnry = new Masonry(gridContainer, {
                    itemSelector: '.grid-item',
                    columnWidth: '.grid-item',
                    percentPosition: true,
                    transitionDuration: '0.4s'
                });
                GLightbox({ selector: '.glightbox', loop: true });
            });
        }

        document.body.addEventListener('htmx:afterOnLoad', function(evt) {
            if (gridContainer && msnry && evt.detail.xhr.responseURL.includes('page=')) {
                imagesLoaded(gridContainer, function() {
                    msnry.reloadItems();
                    msnry.layout();
                    GLightbox({ selector: '.glightbox', loop: true });
                });
            }
        });
    });
})();