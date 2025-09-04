document.addEventListener("DOMContentLoaded", function () {
    const nameInput = document.getElementById("nameFilter");
    const ingredientInput = document.getElementById("ingredientFilter");
    const minPriceInput = document.getElementById("minPrice");
    const maxPriceInput = document.getElementById("maxPrice");
    const sortSelect = document.getElementById("sortBy");
    const availabilitySelect = document.getElementById("availabilityFilter");

    const containers = document.querySelectorAll(".dishes-container");
    if (!containers.length) return;

    function updateContainer(container) {
        let dishes = Array.from(container.querySelectorAll(".dish"));

        // Filter
        dishes.forEach(dish => {
            const name = (dish.dataset.name || "").toLowerCase();
            const ingredients = (dish.dataset.ingredients || "").toLowerCase();
            const price = parseFloat(dish.dataset.price) || 0;

            const matchesName = name.includes(nameInput.value.toLowerCase());

            const searchIngredients = ingredientInput.value.toLowerCase().split(",").map(s => s.trim()).filter(Boolean);
            const ingredientsArray = (dish.dataset.ingredients || "")
                .toLowerCase()
                .split(",")
                .map(s => s.trim());
            const matchesIngredients = searchIngredients.every(term =>
                ingredientsArray.some(ing => ing.startsWith(term))
            );

            const minPrice = parseFloat(minPriceInput.value) || 0;
            const maxPrice = parseFloat(maxPriceInput.value) || Infinity;
            const matchesPrice = price >= minPrice && price <= maxPrice;
            
            const available = (dish.dataset.available || "").toLowerCase(); // lowercase
            const matchesAvailability = 
                availabilitySelect.value === "all" ||
                (availabilitySelect.value === "available" && available === "true") ||
                (availabilitySelect.value === "unavailable" && available === "false");

            dish.style.display = (matchesName && matchesIngredients && matchesPrice && matchesAvailability) ? "" : "none";
        });

        // Sort visible dishes
        const sortCriteria = sortSelect.value;
        const visibleDishes = Array.from(container.querySelectorAll(".dish")).filter(d => d.style.display !== "none");

        if (sortCriteria) {
            visibleDishes.sort((a, b) => {
                let aVal = a.dataset[sortCriteria];
                let bVal = b.dataset[sortCriteria];
                if (sortCriteria === "price") return parseFloat(aVal) - parseFloat(bVal);
                return aVal.localeCompare(bVal);
            });

            visibleDishes.forEach(dish => container.appendChild(dish));
        }

        // Reapply stagger
        visibleDishes.forEach((dish, index) => {
            const row = dish.querySelector(".row");
            if (!row) return;

            if ((index + 1) % 2 === 0) {
                row.classList.add("flex-row-reverse");
            } else {
                row.classList.remove("flex-row-reverse");
            }
        });
    }

    [nameInput, ingredientInput, minPriceInput, maxPriceInput, sortSelect, availabilitySelect].forEach(input => {
        input.addEventListener("input", () => containers.forEach(updateContainer));
        input.addEventListener("change", () => containers.forEach(updateContainer));
    });

    // Initial update
    containers.forEach(updateContainer);
});