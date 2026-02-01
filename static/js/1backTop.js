
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
   

        