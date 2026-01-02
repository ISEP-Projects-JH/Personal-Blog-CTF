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
When running in CTF mode, successful exploitation updates the ``ctf_progress``
table, allowing the system to expose flags through a dedicated API endpoint.

Outside CTF mode, no flag or progress information is revealed and SQLi attempts
will not succeed as the safe library is used.

Summary
-------
This codebase is a **controlled, educational example** designed to show:

* How dependency-level flaws can undermine otherwise clean application code
* Why SQL injection remains a critical and common vulnerability
* How CTF challenges can be structured to enforce specific learning outcomes

It should be studied as a teaching artifact, not used as a security reference.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Form  # python-multipart support
from fastapi import Query

from sqli_ctf import ctf_sql

import time
import hashlib
import jwt

# =========================
# JWT Configuration
# =========================

JWT_SECRET = "dev-secret-for-ctf"

JWT_SECRET_USER = "dev-secret-for-ctf-user"
JWT_SECRET_ADMIN = "dev-secret-for-ctf-admin"
JWT_ALGO = "HS256"

JWT_EXPIRE_SECONDS = 3600  # 1 hour

# =========================
# Internal Constants
# =========================

# User-side secret fragments
USER_MID_1 = "thisisanexample"
USER_MID_2 = "cool"

# Admin-side secret fragments (must be different)
ADMIN_MID_1 = "rootpower"
ADMIN_MID_2 = "adminonly"

ADD_NUM = 0xEEE7


# =========================
# User JWT Helpers
# =========================

def make_user_proof(username: str, email: str, ts: int) -> str:
    """
    Generate a short proof string bound to user identity and login timestamp
    """
    base = f"{username}{USER_MID_1}{email}{USER_MID_2}{ts}"
    h = hashlib.sha256(base.encode()).hexdigest()
    num = int(h, 16) + ADD_NUM
    return hex(num)[2:].upper()[-4:]


def make_user_token(username: str, email: str) -> str:
    """
    Create a signed JWT for a normal user
    """
    ts = int(time.time())
    payload = {
        "role": "user",
        "username": username,
        "email": email,
        "login_ts": ts,
        "proof": make_user_proof(username, email, ts),
        "exp": ts + JWT_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET_USER, algorithm=JWT_ALGO)


def verify_user_token(token: str, username: str) -> dict | None:
    """
    Verify user JWT integrity and bind it to the requested username
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_USER,
            algorithms=[JWT_ALGO],
        )

        if payload.get("role") != "user":
            return None

        if payload["username"] != username:
            return None

        expect = make_user_proof(
            payload["username"],
            payload["email"],
            payload["login_ts"],
        )

        if payload["proof"] != expect:
            return None

        return payload

    except jwt.PyJWTError:
        return None


# =========================
# Admin JWT Helpers
# =========================

def make_admin_proof(username: str, ts: int) -> str:
    """
    Generate a short proof string for admin tokens
    """
    base = f"{username}{ADMIN_MID_1}{ADMIN_MID_2}{ts}"
    h = hashlib.sha256(base.encode()).hexdigest()
    num = int(h, 16) + ADD_NUM
    return hex(num)[2:].upper()[-4:]


def make_admin_token(username: str) -> str:
    """
    Create a signed JWT for admin users
    """
    ts = int(time.time())
    payload = {
        "role": "admin",
        "username": username,
        "login_ts": ts,
        "proof": make_admin_proof(username, ts),
        "exp": ts + JWT_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET_ADMIN, algorithm=JWT_ALGO)


def verify_admin_token(token: str) -> dict | None:
    """
    Verify admin JWT integrity
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_ADMIN,
            algorithms=[JWT_ALGO],
        )

        if payload.get("role") != "admin":
            return None

        expect = make_admin_proof(
            payload["username"],
            payload["login_ts"],
        )

        if payload["proof"] != expect:
            return None

        return payload

    except jwt.PyJWTError:
        return None


# =========================
# Application Setup
# =========================

app = FastAPI(title="Personal Blog Backend")

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    """
    Create a database connection
    """
    return ctf_sql.MySql.connect(
        host=ctf_sql.DB_HOST,
        user=ctf_sql.DB_USER,
        passwd=ctf_sql.DB_PASS,
        db=ctf_sql.DB_NAME,
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

    return [
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

@app.post("/api/login/user")
def login_user(
        email: str = Form(...),
        password: str = Form(...),
):
    conn = None
    cur = None

    try:
        conn = get_conn()
        cur = conn.cursor()

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

        if ctf_sql.SESSION_NAME == ctf_sql.constants.CTF_SESSION_NAME:
            cur.execute("""
                UPDATE ctf_progress
                SET user_pwned = TRUE
                WHERE id = 1
            """)
            conn.commit()

        jwt_ = make_user_token(real_username, email)

        return {
            "success": True,
            "username": real_username,
            "jwt": jwt_,
        }
    except ctf_sql.MySql.MySQLError:

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
        conn = get_conn()
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

        if ctf_sql.SESSION_NAME == ctf_sql.constants.CTF_SESSION_NAME:
            cur.execute("""
                UPDATE ctf_progress
                SET admin_pwned = TRUE
                WHERE id = 1
            """)
            conn.commit()

        admin_jwt = make_admin_token(username)

        return {
            "success": True,
            "username": username,
            "jwt": admin_jwt,
        }

    except ctf_sql.MySql.MySQLError:

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
