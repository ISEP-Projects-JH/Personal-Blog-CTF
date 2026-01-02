const API_BASE = "http://127.0.0.1:8000";

/* =========================
 * Base request wrapper
 * ========================= */

async function apiGet(path) {
    const res = await fetch(API_BASE + path, {
        method: "GET",
        credentials: "omit",
    });

    if (!res.ok) {
        // noinspection ExceptionCaughtLocally
        throw new Error(`GET ${path} failed`);
    }

    return res.json();
}

async function apiPost(path, data) {
    const res = await fetch(API_BASE + path, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams(data),
        credentials: "omit",
    });

    if (!res.ok) {
        // noinspection ExceptionCaughtLocally
        throw new Error(`POST ${path} failed`);
    }

    return res.json();
}

/* =========================
 * User APIs
 * ========================= */

/**
 * Home page: popular articles
 */
async function fetchHome() {
    return apiGet("/api/home");
}
/**
 * User login
 */
async function loginUser(email, password) {
    const res = await apiPost("/api/login/user", {
        email,
        password,
    });

    if (res.success) {
        localStorage.setItem("jwt", res.jwt);
        localStorage.setItem("username", res.username);
    }

    return res;
}

/* =========================
 * Admin APIs (new)
 * ========================= */

/**
 * Admin login
 * POST /api/login/admin
 */
async function loginAdmin(username, password) {
    const res = await apiPost("/api/login/admin", {
        username,
        password,
    });

    if (res.success) {
        localStorage.setItem("admin_jwt", res.jwt);
        localStorage.setItem("admin_username", res.username);
    }

    return res;
}

/**
 * Validate admin JWT
 * GET /api/admin/check?jwt=...
 */
async function checkAdmin() {
    const jwt = localStorage.getItem("admin_jwt");
    if (!jwt) {
        // noinspection ExceptionCaughtLocally
        throw new Error("No admin JWT");
    }

    return apiGet(
        `/api/admin/check?jwt=${encodeURIComponent(jwt)}`
    );
}

window.API = {
    // user
    fetchHome,
    loginUser,

    // admin
    loginAdmin,
    checkAdmin,
};
