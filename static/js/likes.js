document.addEventListener("DOMContentLoaded", function () {
  // 1. Usamos delegación de eventos para que funcione incluso si el HTML cambia
  document.body.addEventListener("click", async function (e) {
    const button = e.target.closest(".like-button");
    if (!button) return;

    e.preventDefault();
    
    const postId = button.dataset.postId;
    const likeUrl = button.dataset.likeUrl;
    const icon = button.querySelector("i");
    // Buscamos el contador cerca del botón
   const likeCountSpan = button.closest(".card-body").querySelector(".like-count");

    try {
      // 2. Usamos FormData para que Django pueda leerlo con request.POST
      const formData = new FormData();
      formData.append("post_id", postId);

      const response = await fetch(likeUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          // NO ponemos Content-Type, el navegador lo configura solo con FormData
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error en el servidor: ${response.status}`);
      }

      const data = await response.json();

      // 3. Actualizamos el Icono
      if (data.liked) {
        icon.classList.replace("bi-heart", "bi-heart-fill");
        icon.classList.add("text-danger");
      } else {
        icon.classList.replace("bi-heart-fill", "bi-heart");
        icon.classList.remove("text-danger");
      }

      // 4. Actualizamos el Contador (usando el nombre 'count' que definimos en la vista)
      if (likeCountSpan) {
        likeCountSpan.textContent = data.count;
      }

    } catch (err) {
      console.error("Detalles del error:", err);
      alert("No se pudo procesar el Me gusta. Revisa la consola (F12).");
    }
  });
});

// Función para leer CSRF token de las cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}