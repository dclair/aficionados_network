document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".btn-like").forEach((button) => {
    button.addEventListener("click", async function (e) {
      e.preventDefault();
      const postId = this.getAttribute("data-post-id");
      const icon = this.querySelector("i");
      const likeCount = this.nextElementSibling;

      try {
        const response = await fetch(this.href, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) throw new Error("Error en la petición");

        const data = await response.json();

        // Actualizar ícono
        if (data.liked) {
          icon.classList.remove("bi-heart");
          icon.classList.add("bi-heart-fill", "text-danger");
        } else {
          icon.classList.remove("bi-heart-fill", "text-danger");
          icon.classList.add("bi-heart");
        }

        // Actualizar contador
        if (likeCount && likeCount.classList.contains("like-count")) {
          likeCount.textContent = data.count;
        }
      } catch (error) {
        console.error("Error:", error);
        if (error.message.includes("401")) {
          window.location.href = "/accounts/login/";
        }
      }
    });
  });
});

// Función auxiliar para obtener el token CSRF
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
