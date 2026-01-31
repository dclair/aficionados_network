/**
 * AJAX MASTER SCRIPT - Hubs & Clicks
 * Gestiona Likes, Seguidores y Asistencia a Eventos
 */

// Función para obtener el CSRF Token (Seguridad de Django)
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); break;
            }
        }
    }
    return cookieValue;
};

document.addEventListener('DOMContentLoaded', () => {

    // --- 1. LÓGICA DE LIKES ---
    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.btn-like-ajax');
        if (!btn) return;
        e.preventDefault();

        const res = await fetch(btn.dataset.url, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': getCookie('csrftoken'), 
                'X-Requested-With': 'XMLHttpRequest' 
            },
            body: JSON.stringify({ id: btn.dataset.id })
        });
        
        if (res.ok) {
            const data = await res.json();
            const icon = btn.querySelector('i');
            icon.className = data.liked ? 'bi bi-heart-fill text-danger' : 'bi bi-heart';
            btn.querySelector('.like-count').textContent = data.total_likes;
        }
    });

    // --- 2. LÓGICA DE SEGUIR (FOLLOW) ---
    const followBtn = document.getElementById('follow-btn');
    if (followBtn) {
        followBtn.addEventListener('click', async function() {
            const formData = new FormData();
            formData.append('profile_pk', this.dataset.profileId);
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

            const res = await fetch(this.dataset.url, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (res.ok) {
                const data = await res.json();
                this.textContent = data.following ? 'Dejar de seguir' : 'Seguir';
                this.className = `btn btn-sm rounded-pill px-4 shadow-sm ${data.following ? 'btn-outline-danger' : 'btn-hubs'}`;
                
                // Actualiza el contador de seguidores si existe en la página
                const counter = document.querySelector('.followers-count-display') || 
                                document.querySelector('[data-bs-target="#followersModal"] strong');
                if (counter) counter.textContent = data.followers_count;
            }
        });
    }

    // --- 3. LÓGICA DE ASISTENCIA (EVENTOS) ---
    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.btn-attendance-ajax') || e.target.closest('#attendance-btn');
        if (!btn) return;
        e.preventDefault();

        const res = await fetch(btn.dataset.url, {
            method: 'POST',
            headers: { 
                'X-CSRFToken': getCookie('csrftoken'), 
                'X-Requested-With': 'XMLHttpRequest' 
            }
        });

        if (res.ok) {
            const data = await res.json();
            
            // Actualizar el botón (texto e iconos)
            if (btn.id === 'attendance-btn') { // Vista detalle
                btn.innerHTML = data.joined ? '<i class="bi bi-x-circle me-2"></i>No podré ir' : '<i class="bi bi-person-plus-fill me-2"></i>¡Me apunto!';
                btn.className = `btn btn-lg w-100 shadow-sm ${data.joined ? 'btn-outline-danger' : 'btn-hubs'}`;
            } else { // Vista lista
                btn.textContent = data.joined ? 'Salir' : 'Unirme';
                btn.className = `btn btn-sm px-3 btn-attendance-ajax ${data.joined ? 'btn-danger' : 'btn-success'}`;
            }

            // Actualizar contador de asistentes
            const counter = document.querySelector('.participants-count-display');
            if (counter) counter.textContent = `${data.count}/${data.max}`;
        }
    });
});