"""
Insert mock data into production database.

This script is safe to run multiple times.
"""

import os
from sqli_ctf import ctf_sql
import pymysql

pymysql.install_as_MySQLdb()
import MySQLdb  # type: ignore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.join(BASE_DIR, "insert_mock.sql")


def main():
    conn = MySQLdb.connect(
        host=ctf_sql.constants.DB_HOST,
        user=ctf_sql.constants.DB_USER,
        passwd=ctf_sql.constants.DB_PASS,
        autocommit=True,
    )

    cur = conn.cursor()

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql = f.read().replace(
            "${prod_db}", ctf_sql.constants.DB_NAME
        )

    print(f"[+] Executing {SQL_FILE}")

    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)

    cur.close()
    conn.close()

    print("[✓] Mock data inserted.")


if __name__ == "__main__":
    main()
