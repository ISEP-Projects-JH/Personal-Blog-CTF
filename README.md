# Personal Blog CTF — Deployment Guide

This document explains how to **set up the environment**, **configure databases**, and **run the backend and frontend** for the Personal Blog CTF demonstration service.

The project supports **two modes**:

* **Production mode** (normal behavior, no flags)
* **CTF mode** (intentionally vulnerable, flags enabled)

Both modes are backed by **separate MySQL databases**.

---

## 1. Prerequisites

### System Requirements

* **Python 3.11**
* **MySQL server**

  * Local or remote
  * `libmysqlclient` is **NOT required**
  * Authentication via username/password
* **Conda or Mamba**

### Notes

* The backend uses **PyMySQL**, not a native MySQL client.
* CORS is **fully open by design**, as this is a teaching example.

---

## 2. Project Structure

```
Personal-Blog-CTF/
├── app/
│   └── main.py
├── frontend/
│   ├── admin.html
│   ├── admin_login.html
│   ├── app.js
│   ├── ctf-widget.js
│   ├── index.html
│   ├── personal_space.html
│   └── style.css
├── scripts/
│   ├── __init__.py
│   ├── db_bootstrap.py
│   ├── init_prod.sql
│   ├── insert_mock.py
│   ├── insert_mock.sql
│   ├── remove_mock.py
│   ├── remove_mock.sql
│   ├── reset_ctf.sql
│   ├── run_init_prod.py
│   └── run_reset_ctf.py
├── sqli_ctf/
│   └── ctf_sql/
├── .gitignore
├── .gitmodules
├── environment.yml
├── project.puml
└── README.md
```

* `sqli_ctf/ctf_sql` is pulled automatically via `.gitmodules`
* No manual installation is required for `ctf_sql`

---

## 3. Environment Setup (Conda)

### Create the environment

```bash
conda env create -f environment.yml
```

or with Mamba:

```bash
mamba env create -f environment.yml
```

### Activate the environment

```bash
conda activate sqli-ctf
```

---

## 4. Database Configuration

The project uses **three sets of credentials**:

### 4.1 MySQL Admin (used only for initialization)

```bash
export MYSQL_ADMIN_HOST=127.0.0.1
export MYSQL_ADMIN_USER=root
export MYSQL_ADMIN_PASS=your_root_password
```

Defaults are used if not set.

---

### 4.2 Production Database

```bash
export DB_HOST=127.0.0.1
export DB_USER=prod_user
export DB_PASS=prod_password
export DB_NAME=prod_db
```

If not exported, defaults are used.

---

### 4.3 CTF Database

```bash
export CTF_DB_HOST=127.0.0.1
export CTF_DB_USER=ctf_user
export CTF_DB_PASS=ctf_password
export CTF_DB_NAME=ctf_db
```

If not exported, defaults are used.

---

## 5. Database Initialization

### 5.1 Bootstrap Users and Databases

Run once to create:

* Production user & database
* CTF user & database

```bash
python scripts/db_bootstrap.py
```

This script behaves the same way as the original `sqli-ctf` setup.

---

### 5.2 Initialize Production Database (Empty)

```bash
python -m scripts.run_init_prod
```

* Creates schema only
* No mock data
* All configuration is taken from environment variables
* Defaults are used if nothing is exported

---

### 5.3 CTF Database Reset (Recommended)

```bash
python -m scripts.run_reset_ctf
```

This will:

1. Drop the existing CTF database
2. Recreate it
3. Insert mock users, posts, and comments
4. Reset CTF progress flags

Running this script is equivalent to a **full CTF reset**.

---

### 5.4 Optional Mock Data Management (Production)

```bash
python -m scripts.insert_mock
```

```bash
python -m scripts.remove_mock
```

These scripts add or remove a **small amount of mock data** in the production database.

---

## 6. Running the Backend

### Select Mode

#### CTF mode (vulnerable behavior, flags enabled)

```bash
export CTF_MODE=ctf
```

on Windows: 
```bash
set CTF_MODE=ctf
```

#### Production mode (safe behavior)

```bash
unset CTF_MODE
```
on Windows: 
```bash
set CTF_MODE=
```

The backend behavior is determined internally by how `ctf_sql` detects this variable.

---

### Start the Backend

From the project root:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at:

```
http://localhost:8000
```

---

## 7. Running the Frontend

In a separate terminal:

```bash
cd frontend
python -m http.server 8080
```

Frontend will be available at:

```
http://localhost:8080
```

---

## 8. CORS Policy

* CORS is **fully open** (`allow_origins=["*"]`)
* This is intentional
* No additional protection is implemented
* The project is a **demonstration service**, not a hardened deployment

---

## 9. Summary

To run the project:

1. Install MySQL
2. Create and activate the conda environment
3. Configure database credentials (or use defaults)
4. Run `db_bootstrap.py`
5. Initialize production and/or reset CTF database
6. Select CTF or production mode
7. Start backend and frontend

This codebase is designed for **education and controlled experimentation**, not for production use.
