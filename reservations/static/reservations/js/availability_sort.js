document.addEventListener('DOMContentLoaded', () => {
    const list = document.getElementById('availability-list');
    if (!list) return;

    const sortDirection = { table: true, seats: true, slots: true };

    function sortList(attribute) {
        const items = Array.from(list.querySelectorAll('.list-group-item'));
        items.sort((a, b) => {
            const aVal = Number(a.dataset[attribute]) || 0;
            const bVal = Number(b.dataset[attribute]) || 0;
            if (attribute == "slots")
                return sortDirection[attribute] ? bVal - aVal : aVal - bVal;
            return sortDirection[attribute] ? aVal - bVal : bVal - aVal;
        });
        items.forEach(item => list.appendChild(item));
        sortDirection[attribute] = !sortDirection[attribute]; // toggle direction
    }

    // Map select values directly to dataset attributes
    const valueMap = {
        number: 'table',
        seats: 'seats',
        slots: 'slots'
    };

    const sortSelect = document.getElementById('sortTable');
    sortSelect.addEventListener('change', () => {
        sortList(valueMap[sortSelect.value]);
    });
});