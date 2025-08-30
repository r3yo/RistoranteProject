document.addEventListener("DOMContentLoaded", function() {
    const wrapper = document.getElementById("notif-wrapper");
    const jsonUrl = wrapper.getAttribute("data-json-url");
    const markUrl = wrapper.getAttribute("data-mark-url");

    const notifList = document.getElementById("notif-list");
    const unreadCountElem = document.getElementById("unread-count");
    const dropdown = document.getElementById("notif-dropdown");
    const toggleBtn = document.getElementById("notif-toggle");
    const markAllBtn = document.getElementById("mark-all-read");

    // --- WebSocket for real-time notifications ---
    const ws = new WebSocket(
        (window.location.protocol === "https:" ? "wss" : "ws") +
        "://" + window.location.host + "/ws/notifications/"
    );

    ws.onmessage = function(e) {
        const data = JSON.parse(e.data);

        const li = document.createElement("li");
        li.textContent = data.message + " (" + data.type + ")";
        notifList.prepend(li);

        unreadCountElem.textContent = parseInt(unreadCountElem.textContent || "0") + 1;
    };

    // --- Load existing notifications via AJAX ---
    async function loadNotifications() {
        const response = await fetch(jsonUrl);
        const data = await response.json();

        notifList.innerHTML = "";

        data.forEach(n => {
            const li = document.createElement("li");
            li.textContent = n.message;
            notifList.appendChild(li);
        });

        unreadCountElem.textContent = data.length;
    }

    // --- Mark all notifications as read ---
    async function markAllRead() {
        const response = await fetch(markUrl);

        if (!response.ok) { // Check http status
            console.error("Network error when marking notifications read");
            return;
        }

        const result = await response.json();

        if (result.status === "ok") {
            notifList.innerHTML = "";
            unreadCountElem.textContent = "0";
        } else {
            console.error("Failed to mark notifications as read:", result);
        }
    }

    // --- Dropdown toggle ---
    toggleBtn.addEventListener('click', function() {
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';

        if (dropdown.style.display === 'none') {
            markAllRead();  // ✅ just call the existing function
        }
    });

    // --- Button click for marking all as read ---
    markAllBtn.addEventListener('click', markAllRead);

    // Load notifications immediately on page load
    loadNotifications();
});