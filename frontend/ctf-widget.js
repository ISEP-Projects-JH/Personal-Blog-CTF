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
     * Styles
     * ========================= */

    const style = document.createElement("style");
    style.innerHTML = `
        #ctf-widget {
            position: fixed;
            top: 16px;
            right: 16px;
            z-index: 9999;
            font-family: monospace;
        }

        .ctf-main {
            background: #111;
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: default;
            display: flex;
            gap: 8px;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        .ctf-title {
            font-weight: bold;
        }

        .ctf-status {
            opacity: 0.9;
        }

        .ctf-disabled {
            background: #444;
            color: #bbb;
        }

        .ctf-tooltip {
            display: none;
            margin-top: 6px;
            background: #222;
            color: #eee;
            padding: 8px 10px;
            border-radius: 6px;
            font-size: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        #ctf-widget:hover .ctf-tooltip {
            display: block;
        }

        .ctf-flag-ok {
            color: #4caf50;
        }

        .ctf-flag-no {
            color: #f44336;
        }

        .ctf-progress {
            height: 6px;
            background: #333;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 4px;
        }

        .ctf-progress-bar {
            height: 100%;
            background: #4caf50;
            width: 0%;
        }
        .ctf-row {
            display: grid;
            grid-template-columns: 60px 1fr;
            align-items: center;
        }
        
        .ctf-label {
            text-align: left;
        }
        
        .ctf-star {
            text-align: left;
        }
    `;
    document.head.appendChild(style);

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
