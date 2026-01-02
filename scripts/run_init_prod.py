"""
Run init_prod.sql using production database credentials.

This script initializes the production schema and initial data.
It is NOT destructive and should normally be run once.
"""

import os
from sqli_ctf import ctf_sql
import pymysql

pymysql.install_as_MySQLdb()

import MySQLdb  # type: ignore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.join(BASE_DIR, "init_prod.sql")


def main():
    conn = MySQLdb.connect(
        host=ctf_sql.constants.DB_HOST,
        user=ctf_sql.constants.DB_USER,
        passwd=ctf_sql.constants.DB_PASS,
        autocommit=True,
    )

    cur = conn.cursor()

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_raw = f.read()
        sql = sql_raw.replace("${prod_db}", ctf_sql.constants.DB_NAME)

    print(f"[+] Executing {SQL_FILE}")

    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if not stmt:
            continue
        cur.execute(stmt)

    cur.close()
    conn.close()

    print("[✓] Production database initialized.")


if __name__ == "__main__":
    main()
