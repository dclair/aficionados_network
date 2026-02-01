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

/**
 * Validación de Formularios de Bootstrap 5
 * Busca cualquier formulario con la clase .needs-validation y detiene el envío
 * si los campos no son válidos, mostrando los errores visuales.
 */
(function () {
    'use strict'
    
    // Escuchamos el evento de carga del DOM para asegurar que los elementos existen
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


// CON ESTO SE INICIALIZA EL MASONRY galeria de imagenes,
// Usamos una función autoejecutable para proteger las variables
(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        console.log('Community Hub JS: Cargado y listo.');

        // ==============================================
        // 1. INICIALIZACIÓN DE LA GALERÍA MASONRY
        // ==============================================
        const gridContainer = document.querySelector('.clicks-grid');
        let msnry; // Variable "global" dentro de este ámbito para acceder luego

        // Solo ejecutamos si estamos en la página de la galería
        if (gridContainer) {
            console.log('Galería detectada. Iniciando Masonry...');

            // Esperamos a que las imágenes de la carga inicial estén listas
            imagesLoaded(gridContainer, function() {
                msnry = new Masonry(gridContainer, {
                    itemSelector: '.grid-item',
                    columnWidth: '.grid-item', // Usa el ancho del ítem como base
                    percentPosition: true,     // Importante para diseño responsivo
                    transitionDuration: '0.4s' // Animación suave al reordenar
                });

                // Inicializamos el Lightbox para las primeras fotos
                GLightbox({ selector: '.glightbox', loop: true });
                console.log('Masonry inicializado correctamente.');
            });
        }

        // ==============================================
        // 2. ESCUCHA DE HTMX (EL SCROLL INFINITO) - ¡LA CLAVE AQUÍ!
        // ==============================================
        document.body.addEventListener('htmx:afterOnLoad', function(evt) {
            // Verificamos si la petición que acaba de terminar es la de la galería
            // Buscamos si la URL de la petición contiene "page=" (indicador de paginación)
            // Y nos aseguramos de que el grid existe en esta página.
            if (gridContainer && msnry && evt.detail.xhr.responseURL.includes('page=')) {
                console.log('HTMX ha traído nuevas fotos. Reordenando Masonry...');

                // ¡IMPORTANTE! Esperar a que las NUEVAS imágenes se descarguen
                imagesLoaded(gridContainer, function() {
                    // 1. Dile a Masonry que busque los elementos nuevos en el DOM
                    msnry.reloadItems();
                    // 2. Dile a Masonry que recalcule todas las posiciones
                    msnry.layout();

                    // 3. Reinicializa GLightbox para que las fotos nuevas se puedan ampliar
                    GLightbox({ selector: '.glightbox', loop: true });

                    console.log('Masonry reordenado y Lightbox actualizado.');
                });
            }
        });

        // ==============================================
        // 3. OTRAS FUNCIONALIDADES DEL HUB (Ej: Botón volver arriba)
        // ==============================================
        // ... el resto de tu código para el botón, si lo tienes ...
    });
})();