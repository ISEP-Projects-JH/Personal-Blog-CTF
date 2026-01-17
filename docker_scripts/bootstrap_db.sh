#!/usr/bin/env bash
set -e

echo "[*] Preparing MariaDB directories..."
mkdir -p /var/run/mysqld
chown -R mysql:mysql /var/run/mysqld /var/lib/mysql

echo "[*] Starting MariaDB (build-time)..."
mariadbd-safe \
  --user=mysql \
  --bind-address=127.0.0.1 \
  --port=3306 &

# 等待数据库可用
echo "[*] Waiting for MariaDB..."
for i in {1..30}; do
  if mariadb-admin ping >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "[*] Configuring root authentication..."
mariadb -u root <<EOF
ALTER USER 'root'@'localhost'
  IDENTIFIED VIA mysql_native_password
  USING PASSWORD('');
FLUSH PRIVILEGES;
EOF

echo "[*] Running database bootstrap scripts..."
python -m scripts.db_bootstrap
python -m scripts.run_reset_ctf

echo "[*] Shutting down MariaDB..."
mariadb-admin shutdown

echo "[✓] Database bootstrap completed."
