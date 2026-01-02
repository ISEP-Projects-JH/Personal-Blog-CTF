(function () {
    /* =========================
     * Configuration
     * ========================= */

    const API_URL = "http://127.0.0.1:8000/api/flags";

    /* =========================
     * DOM Construction
     * ========================= */

    // Create main widget container
    const widget = document.createElement("div");
    widget.id = "ctf-widget";
    widget.innerHTML = `
        <div class="ctf-main">
            <span class="ctf-title">CTF</span>
            <span class="ctf-status">Loading...</span>
        </div>
        <div class="ctf-tooltip"></div>
    `;
    document.body.appendChild(widget);

    /* =========================
     * Logic
     * ========================= */

    fetch(API_URL)
        .then(res => res.json())
        .then(data => {
            // Unpack top-level response fields
            const {ctf_enabled, flags} = data;

            const status = widget.querySelector(".ctf-status");
            const tooltip = widget.querySelector(".ctf-tooltip");
            const main = widget.querySelector(".ctf-main");

            // CTF disabled (simulate production mode)
            if (!ctf_enabled) {
                main.classList.add("ctf-disabled");
                status.textContent = "Simulated Production Mode";
                tooltip.innerHTML = "SQL injection is not possible";
                return;
            }

            // Unpack flags object
            const {
                flags_obtained,
                total_flags,
                user_pwned,
                admin_pwned
            } = flags;

            const percent = (flags_obtained / total_flags) * 100;

            status.textContent = `Progress ${flags_obtained} / ${total_flags}`;

            tooltip.innerHTML = `
                <div class="ctf-row">
                    <span class="ctf-label">User</span>
                    <span class="ctf-star ${user_pwned ? "ctf-flag-ok" : "ctf-flag-no"}" style="font-size: 1.25em;">
                        ${user_pwned ? "★" : "☆"}
                    </span>
                </div>
                <div class="ctf-row">
                    <span class="ctf-label">Admin</span>
                    <span class="ctf-star ${admin_pwned ? "ctf-flag-ok" : "ctf-flag-no"}" style="font-size: 1.25em;">
                        ${admin_pwned ? "★" : "☆"}
                    </span>
                </div>
                <div class="ctf-progress">
                    <div class="ctf-progress-bar" style="width:${percent}%"></div>
                </div>
            `;

        })
        .catch(() => {
            // API unavailable or network error
            const status = widget.querySelector(".ctf-status");
            status.textContent = "CTF unavailable";
        });
})();
