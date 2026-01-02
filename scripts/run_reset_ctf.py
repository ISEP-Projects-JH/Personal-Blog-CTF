"""
Run reset_ctf.sql using CTF database credentials.

This script DROPS and recreates the CTF database.
"""

import os
from sqli_ctf import ctf_sql
import pymysql

pymysql.install_as_MySQLdb()

import MySQLdb  # type: ignore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.join(BASE_DIR, "reset_ctf.sql")


def main():
    conn = MySQLdb.connect(
        host=ctf_sql.constants.CTF_DB_HOST,
        user=ctf_sql.constants.CTF_DB_USER,
        passwd=ctf_sql.constants.CTF_DB_PASS,
        autocommit=True,
    )

    cur = conn.cursor()

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_raw = f.read()
        sql = sql_raw.replace("${ctf_db}", ctf_sql.constants.CTF_DB_NAME)

    print(f"[+] Executing {SQL_FILE}")

    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)

    cur.execute(f"USE {ctf_sql.constants.CTF_DB_NAME}")

    checks = [
        "SELECT COUNT(*) FROM users",
        "SELECT COUNT(*) FROM admins",
        "SELECT COUNT(*) FROM posts",
        "SELECT COUNT(*) FROM comments",
        "SELECT COUNT(*) FROM ctf_progress",
    ]

    for q in checks:
        cur.execute(q)
        print(q, "=>", cur.fetchone()[0])

    cur.close()
    conn.close()

    print("[✓] CTF database reset and verified.")


if __name__ == "__main__":
    main()
