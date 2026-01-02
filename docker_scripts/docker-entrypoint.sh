#!/usr/bin/env bash
set -e

echo "[+] Container started"

# --------------------------------------
# Optional automatic database initialization
# --------------------------------------
if [ "${AUTO_DB_INIT:-0}" = "1" ]; then
    echo "[+] AUTO_DB_INIT enabled"

    echo "[+] Running database bootstrap..."
    python -m scripts.db_bootstrap

    echo "[+] Initializing production database schema..."
    python -m scripts.run_init_prod

    if [ "${CTF_MODE:-}" = "ctf" ]; then
        echo "[+] CTF_MODE=ctf detected, resetting CTF database..."
        python -m scripts.run_reset_ctf
    else
        echo "[+] CTF_MODE not set or not 'ctf', skipping CTF reset"
    fi

    echo "[✓] Database initialization completed"
else
    echo "[i] AUTO_DB_INIT not enabled, skipping database initialization"
fi

# --------------------------------------
# Start backend and frontend
# --------------------------------------

echo "[+] Starting backend (FastAPI on :8000)..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

echo "[+] Starting frontend (http.server on :8080)..."
cd frontend
exec python -m http.server 8080
