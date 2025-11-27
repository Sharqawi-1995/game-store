document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const cards = document.querySelectorAll("#games-container .card");

    if (!searchInput) return;

    searchInput.addEventListener("keyup", function () {
        const query = searchInput.value.toLowerCase();

        cards.forEach(card => {
            const title = card.querySelector(".card-title").textContent.toLowerCase();
            if (title.includes(query)) {
                card.parentElement.style.display = ""; // show column
            } else {
                card.parentElement.style.display = "none"; // hide column
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(".game-card");

    cards.forEach(card => {
        card.addEventListener("click", function (e) {
            // Prevent clicks on buttons/forms inside the card from triggering navigation
            if (e.target.tagName.toLowerCase() === "button" || e.target.closest("form")) {
                return;
            }

            const gameId = this.getAttribute("data-id");
            if (gameId) {
                window.location.href = `/game/${gameId}/`;  // Django detail URL
            }
        });
    });
});