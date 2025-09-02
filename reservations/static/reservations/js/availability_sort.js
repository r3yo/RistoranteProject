document.addEventListener('DOMContentLoaded', () => {
    const list = document.getElementById('availability-list');
    console.log("List element:", list);
    if (!list) return;

    const sortDirection = { table: true, seats: true, slots: true };

    function sortList(attribute) {
        const items = Array.from(list.querySelectorAll('.list-group-item'));
        items.sort((a, b) => {
            const aVal = Number(a.dataset[attribute]) || 0;
            const bVal = Number(b.dataset[attribute]) || 0;
            return sortDirection[attribute] ? aVal - bVal : bVal - aVal;
        });
        items.forEach(item => list.appendChild(item));
        sortDirection[attribute] = !sortDirection[attribute];
    }

    document.getElementById('sort-table-number').addEventListener('click', () => sortList('table'));
    document.getElementById('sort-seats').addEventListener('click', () => sortList('seats'));
    document.getElementById('sort-slots').addEventListener('click', () => sortList('slots'));
});