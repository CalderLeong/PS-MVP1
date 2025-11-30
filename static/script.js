// static/script.js – PillowStocks Interactive Engine
console.log("PillowStocks JS loaded – interactivity ON");

// ==== 1. Theme Toggle ====
const toggle = document.getElementById("themeToggle");

function updateToggleIcon() {
    if (document.body.classList.contains("dark-mode")) {
        toggle.textContent = "☀️";
    } else {
        toggle.textContent = "🌙";
    }
}

toggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    updateToggleIcon();
    localStorage.setItem("theme", document.body.classList.contains("dark-mode") ? "dark" : "light");
});

// On page load
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
    }
    updateToggleIcon();
});

// ==== 2. Auto-refresh dashboard every 5 minutes (live edge) ====
let refreshCount = 0;
function autoRefresh() {
    if (window.location.pathname === "/") {
        refreshCount++;
        const status = document.getElementById("refresh-status");
        if (status) status.textContent = `Auto-refresh #${refreshCount} • ${new Date().toLocaleTimeString()}`;
        window.location.reload();
    }
}
// Start 5-minute cycle (300000 ms)
setInterval(autoRefresh, 300000);

// ==== 3. Real-time search with instant add (no full reload) ====
const searchForm = document.querySelector(".search-form");
if (searchForm) {
    const input = searchForm.querySelector("input[name='add_ticker']");
    
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            const ticker = input.value.trim().toUpperCase();
            if (ticker && ticker.length >= 1 && ticker.length <= 5) {
                // Visual feedback
                input.style.background = "rgba(255,139,167,0.2)";
                setTimeout(() => {
                    searchForm.submit(); // now reloads with new ranking
                }, 300);
            }
        }
    });
}

// ==== 4. Hover animations + micro-interactions on cards ====
document.querySelectorAll(".card").forEach(card => {
    card.style.transition = "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)";
    
    card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-12px) scale(1.02)";
        card.style.boxShadow = "0 25px 50px rgba(179, 107, 84, 0.4)";
    });
    
    card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0) scale(1)";
        card.style.boxShadow = "0 8px 25px var(--shadow)";
    });
    
    // Click a card → copy ticker to clipboard + flash
    card.addEventListener("click", () => {
        const ticker = card.querySelector(".ticker").textContent;
        navigator.clipboard.writeText(ticker);
        
        const flash = document.createElement("div");
        flash.textContent = `Copied ${ticker}`;
        flash.style.cssText = `
            position: fixed; top: 20px; right: 20px; 
            background: var(--accent); color: white; 
            padding: 12px 20px; border-radius: 50px; 
            z-index: 9999; font-weight: 600;
            animation: fadeOut 2s forwards;
        `;
        document.body.appendChild(flash);
        setTimeout(() => flash.remove(), 2000);
    });
});

// Add fade-out animation
const style = document.createElement("style");
style.textContent = `
@keyframes fadeOut {
    0% { opacity: 1; transform: translateY(0); }
    100% { opacity: 0; transform: translateY(-20px); }
}
.card { cursor: pointer; }
`;
document.head.appendChild(style);

// ==== 5. Live clock in footer ====
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    const dateStr = now.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" });
    const clock = document.getElementById("live-clock");
    if (clock) clock.textContent = `${dateStr} • ${timeStr}`;
}
updateClock();
setInterval(updateClock, 1000);

// ==== 6. Instant add without full reload (feels like magic) =====
document.querySelector(".search-form")?.addEventListener("submit", function(e) {
    const input = this.querySelector("input");
    if (input.value.trim()) {
        input.style.background = "rgba(255, 139, 167, 0.2)";
    }
});