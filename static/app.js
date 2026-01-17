/*
====================================================
CTF Notice:

If you can read this file, frontend restrictions
are no longer relevant.

You are expected to construct your own JavaScript
request (fetch / XMLHttpRequest) to interact with
backend APIs directly.

Server-side filtering is enabled.
The following patterns are BLOCKED:

['OR', '=', '>', '<', 'LIKE', 'IN', 'BETWEEN',
 'TRUE', 'FALSE', '--', "'#", " #"]

NO '|' allowed for USER and NO 'AND' allowed for ADMIN

Regex-based rules exist and are intentionally
not disclosed.

However:
- AND-based logic is still possible for USER in the backend
- There exists a relatively simple solution

Bruteforce is not required.
Think carefully about SQL(MySQL) parsing behavior.

====================================================
*/


const API_BASE = "";

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

function hasIllegalKeyword(input) {
    return /and/i.test(input);
}

/**
 * User login
 */
async function loginUser(email, password) {
    if (hasIllegalKeyword(email)) {
        alert("Invalid email format");
        return;
    }

    const res = await apiPost("/api/login/user", {
        email,
        password,
    });

    const {success, jwt, username} = res

    if (success) {
        localStorage.setItem("jwt", jwt);
        localStorage.setItem("username", username);
    }

    return res;
}

/**
 * Validate user JWT
 * GET /api/user/{username}?jwt=...
 */
async function checkUser(username, jwt) {
    if (!username || !jwt) {
        throw new Error("Missing user credentials");
    }

    const res = await fetch(
        `/api/user/${encodeURIComponent(username)}?jwt=${encodeURIComponent(jwt)}`,
        {
            method: "GET",
            credentials: "omit",
        }
    );

    if (!res.ok) {
        // noinspection ExceptionCaughtLocally
        throw new Error("Unauthorized");
    }

    return res.json();
}

/**
 * Admin login
 * POST /api/login/admin
 */
async function loginAdmin(admin_username, password) {

    const res = await apiPost("/api/login/admin", {
        username: admin_username,
        password: password,
    });

    const {success, jwt, username} = res

    if (success) {
        localStorage.setItem("admin_jwt", jwt);
        localStorage.setItem("admin_username", username);
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
    loginUser,
    checkUser,

    // admin
    loginAdmin,
    checkAdmin,
};
