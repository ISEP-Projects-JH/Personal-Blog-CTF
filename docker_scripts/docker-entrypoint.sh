#!/bin/sh
set -e

echo "[*] Preparing MariaDB runtime directories..."
mkdir -p /var/run/mysqld
chown -R mysql:mysql /var/run/mysqld /var/lib/mysql

echo "[*] Starting MariaDB (runtime)..."
mariadbd-safe \
  --user=mysql \
  --bind-address=0.0.0.0 \
  --port=3306 &

echo "[*] Waiting for MariaDB to be ready..."
until mariadb-admin ping >/dev/null 2>&1; do
  sleep 1
done

echo "[*] Starting FastAPI..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000
