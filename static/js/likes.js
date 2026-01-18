document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".like-button").forEach((button) => {
    button.addEventListener("click", async function (e) {
      e.preventDefault();
      const postId = this.dataset.postId;
      const likeUrl = this.dataset.likeUrl;
      const icon = this.querySelector("i");
      const likeCount = this.closest(".card").querySelector(".like-count");

      try {
        const response = await fetch(likeUrl, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ post_id: postId }),
        });

        const data = await response.json();

        if (data.liked) {
          icon.classList.remove("bi-heart");
          icon.classList.add("bi-heart-fill", "text-danger");
        } else {
          icon.classList.remove("bi-heart-fill", "text-danger");
          icon.classList.add("bi-heart");
        }

        if (likeCount) likeCount.textContent = data.count + " me gusta";

      } catch (err) {
        console.error(err);
        alert("No se pudo procesar el Me gusta.");
      }
    });
  });
});

// Función para leer CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
