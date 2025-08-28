document.addEventListener("DOMContentLoaded", function() {

    const dateInput = document.getElementById("reservation-date");
    const timeSelect = document.getElementById("reservation-time");

    // Function to filter past times for today
    function filterTimes() {
        const selectedDate = new Date(dateInput.value);
        const today = new Date();

        Array.from(timeSelect.options).forEach(option => option.disabled = false); // reset

        if (selectedDate.toDateString() === today.toDateString()) {
            const currentHour = today.getHours();

            Array.from(timeSelect.options).forEach(option => {
                const optionHour = parseInt(option.value.split(":")[0]);
                if (optionHour <= currentHour) {
                    option.disabled = true;
                    option.selected = false;
                }
            });
        }
    }

    // Function to enforce consecutive hours
    function enforceConsecutive() {
        const selected = Array.from(timeSelect.selectedOptions).map(opt => parseInt(opt.value));
        selected.sort((a, b) => a - b);

        if (selected.length <= 1) return;

        let consecutive = true;
        for (let i = 1; i < selected.length; i++) {
            if (selected[i] !== selected[i - 1] + 1) {
                consecutive = false;
                break;
            }
        }

        if (!consecutive) {
            alert("Please select consecutive hours without gaps.");
            const lastSelected = selected[selected.length - 1];
            Array.from(timeSelect.options).forEach(opt => {
                if (parseInt(opt.value) === lastSelected) opt.selected = false;
            });
        }
    }

    // Events
    dateInput.addEventListener("change", filterTimes);
    timeSelect.addEventListener("change", enforceConsecutive);

    // Run once on page load
    filterTimes();
});