document.addEventListener('DOMContentLoaded', () => {
    const list = document.getElementById('availability-list');
    if (!list) return;

    const sortDirection = {
        table: true,
        seats: true,
        slots: true
    };

    function sortList(attribute) {

        const items = Array.from(list.querySelectorAll('.table-item'));

        items.sort((a, b) => {
            const aVal = Number(a.dataset[attribute]) || 0;
            const bVal = Number(b.dataset[attribute]) || 0;

            return sortDirection[attribute] ? aVal - bVal : bVal - aVal;
        });

        // Reattach items in sorted order
        items.forEach(item => list.appendChild(item));

        // Toggle sorting direction
        sortDirection[attribute] = !sortDirection[attribute];
    }

    // Button event listeners
    document.getElementById('sort-table-number').addEventListener('click', () => sortList('table'));
    document.getElementById('sort-seats').addEventListener('click', () => sortList('seats'));
    document.getElementById('sort-slots').addEventListener('click', () => sortList('slots'));
});