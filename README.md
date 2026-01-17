# Personal Blog CTF — Unified Deployment & Design Guide

This repository provides a **self-contained, teaching-oriented SQL injection CTF service** built around a simplified personal blog application.

The project is designed as a **controlled demonstration artifact**, not a production system.
Its primary goal is to illustrate how **security failures can arise from dependency behavior**, even when application-level business logic appears clean and reasonable.

---

## 1. Project Status and Scope

### Current Project State

This project has moved to a **CTF-first, container-first model**:

* Frontend and backend run **together**
* CTF behavior is **always enabled**
* The Docker image is a **fully initialized, ready-to-run CTF instance**
* No runtime database provisioning is expected or supported in Docker mode

Local (non-Docker) execution is still possible for development and study, but **Docker is the authoritative deployment form**.

---

## 2. Enforced CTF Mode

CTF behavior is locked programmatically at process startup:

```python
import builtins
builtins.CTF_MODE = "ctf"
```

This guarantees:

* No dependency on environment variables to select mode
* No accidental fallback to production-safe behavior
* Deterministic SQL execution semantics
* Reproducible exploitation paths

This project does **not** support runtime switching between production and CTF modes.

---

## 3. Architecture Overview

### Runtime Model (Docker)

```
Browser
  │
  ▼
FastAPI (API + HTML + static assets)
  │
  ▼
ctf_sql.MySql (CTF backend)
  │
  ▼
MariaDB (inside container)
```

### Key Characteristics

* Single-origin deployment (same host, same port)
* No reliance on frontend restrictions
* Database behavior is controlled at the driver layer
* Business logic remains readable and uncluttered

---

## 4. Database Connection Design

All database access is routed through a single helper:

```python
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
```

### Why This Matters

* SQL queries look normal and idiomatic
* No SQL string manipulation in business code
* Vulnerability behavior is injected **only at connection time**
* The application logic itself remains easy to audit and reason about

Example usage:

```python
conn = get_conn(sanitize_email)
cur = conn.cursor()
```

This preserves the **readability and intent of the business logic**, while still allowing controlled exploitation.

---

## 5. Partial Sanitization (Updated Behavior)

Earlier iterations supported only “all blocked” or “nothing blocked”.

The current design supports **partial, selective sanitization**, allowing challenge authors to:

* Block trivial payloads (e.g. `AND 1=1 --`)
* Preserve intentional SQL injection paths
* Require participants to understand:

  * Validation logic
  * Dependency behavior
  * Query construction

These checks are **not security features**.
They exist solely to shape the learning experience.

---

## 6. Environment Variables (Runtime Configuration)

### 6.1 Runtime-Configurable Variables

These variables **may be overridden at container startup**:

```bash
JWT_SECRET_USER
JWT_SECRET_ADMIN
JWT_ALGO
JWT_EXPIRE_SECONDS

USER_MID_1
USER_MID_2
ADMIN_MID_1
ADMIN_MID_2
ADD_NUM

ADMIN_URL
ADMIN_LOGIN_URL
```

They affect:

* Token generation
* Proof logic
* URL exposure
* Session behavior

---

### 6.2 Database Variables (NOT Runtime-Configurable in Docker)

The following variables **must NOT be overridden when running the Docker image**:

```bash
DB_HOST
DB_USER
DB_PASS
DB_NAME

CTF_DB_HOST
CTF_DB_USER
CTF_DB_PASS
CTF_DB_NAME
```

#### Why?

* These values are **consumed at build time**
* During image build:

  * Databases are created
  * Users are created
  * Schemas and CTF data are initialized
* The resulting database state is **baked into the image**

Overriding these variables at runtime would point the application to databases that:

* Do not exist
* Do not contain the expected schema
* Break the CTF guarantees

> **This behavior is intentionally different from local development.**

---

## 7. Local Development vs Docker (Important Distinction)

### Local (Non-Docker) Execution

* You may override `DB_*` / `CTF_DB_*`
* You must manually run:

  * `db_bootstrap`
  * `run_reset_ctf`
* The database lifecycle is external and explicit

### Docker Execution (Recommended)

* Database is internal to the container
* Initialization happens **once, at build time**
* Database configuration is frozen
* Runtime configuration is limited to secrets and routing

The Docker image should be treated as a **complete CTF artifact**, not a flexible service.

---

## 8. Docker Build

```bash
docker build -t personal-blog-ctf .
```

The build process:

* Starts MariaDB internally
* Bootstraps users and databases
* Inserts CTF data
* Resets flags
* Shuts down the database
* Freezes the resulting state into the image

---

## 9. Docker Run

```bash
docker run -p 8000:8000 \
  -e JWT_SECRET_USER=example_user_secret \
  -e JWT_SECRET_ADMIN=example_admin_secret \
  -e ADMIN_URL=/admin_hidden \
  -e ADMIN_LOGIN_URL=/login_hidden \
  personal-blog-ctf
```

The service will be available at:

```
http://localhost:8000
```

---

## 10. Security Model (Explicitly Non-Production)

This project intentionally violates real-world security practices:

* Open CORS
* Weak token proof logic
* Controlled SQL injection
* Information disclosure
* Simplified authentication

These choices are **deliberate**.

> This codebase must not be used as a security reference.

---

## 11. Educational Focus

This project demonstrates that:

* Clean business logic does not imply security
* Dependencies are part of the attack surface
* Partial validation often creates exploitable gaps
* Frontend restrictions do not provide real protection

**Security maintenance is essential.**

---

## 12. Intended Audience

This project is intended for:

* CTF players
* Security learners
* Educators
* Challenge authors

It is **not intended** for production deployment or best-practice reference.

---

## Summary

* Frontend and backend run together
* Docker provides a complete, frozen CTF environment
* Database configuration is fixed at build time
* Runtime overrides are limited and intentional
* Vulnerabilities are deliberate and controlled
* Business logic remains readable and unpolluted

This repository should be studied as a **teaching artifact**, not reused as a security solution.
