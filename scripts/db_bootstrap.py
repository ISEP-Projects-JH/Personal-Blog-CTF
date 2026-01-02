"""
Database bootstrap helper.

This script is intended to be run ONCE when the project is first installed.
It creates MySQL users and databases for both:

1. Production / normal environment
2. SQLi-CTF environment

It does NOT create tables or insert any data.
"""

import os
import pymysql

pymysql.install_as_MySQLdb()

import MySQLdb  # type: ignore


def getenv(name: str, default: str) -> str:
    return os.getenv(name, default)


# ---------------------------------------------------------------------------
# MySQL root / admin credentials (used only for bootstrap)
# ---------------------------------------------------------------------------

MYSQL_ADMIN_HOST = getenv("MYSQL_ADMIN_HOST", "127.0.0.1")
MYSQL_ADMIN_USER = getenv("MYSQL_ADMIN_USER", "root")
MYSQL_ADMIN_PASS = getenv("MYSQL_ADMIN_PASS", "")

# ---------------------------------------------------------------------------
# Production configuration
# ---------------------------------------------------------------------------

DB_HOST = getenv("DB_HOST", "127.0.0.1")
DB_USER = getenv("DB_USER", "prod_user")
DB_PASS = getenv("DB_PASS", "")
DB_NAME = getenv("DB_NAME", "prod_db")

# ---------------------------------------------------------------------------
# CTF configuration
# ---------------------------------------------------------------------------

CTF_DB_HOST = getenv("CTF_DB_HOST", "127.0.0.1")
CTF_DB_USER = getenv("CTF_DB_USER", "ctf_user")
CTF_DB_PASS = getenv("CTF_DB_PASS", "")
CTF_DB_NAME = getenv("CTF_DB_NAME", "ctf_db")


def exec_sql(cursor, sql: str) -> None:
    print(f"[+] {sql}")
    cursor.execute(sql)


def setup_database(cursor, db_name: str) -> None:
    exec_sql(
        cursor,
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )


def setup_user(cursor, user: str, password: str, host: str) -> None:
    exec_sql(
        cursor,
        f"CREATE USER IF NOT EXISTS '{user}'@'{host}' IDENTIFIED BY '{password}'"
    )


def grant_privileges(cursor, user: str, host: str, db_name: str) -> None:
    exec_sql(
        cursor,
        f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{user}'@'{host}'"
    )


def main() -> None:
    conn = MySQLdb.connect(
        host=MYSQL_ADMIN_HOST,
        user=MYSQL_ADMIN_USER,
        passwd=MYSQL_ADMIN_PASS,
        autocommit=True,
    )

    cur = conn.cursor()

    # Production
    setup_database(cur, DB_NAME)
    setup_user(cur, DB_USER, DB_PASS, DB_HOST)
    grant_privileges(cur, DB_USER, DB_HOST, DB_NAME)

    # CTF
    setup_database(cur, CTF_DB_NAME)
    setup_user(cur, CTF_DB_USER, CTF_DB_PASS, CTF_DB_HOST)
    grant_privileges(cur, CTF_DB_USER, CTF_DB_HOST, CTF_DB_NAME)

    exec_sql(cur, "FLUSH PRIVILEGES")

    cur.close()
    conn.close()

    print("[✓] Database bootstrap completed.")


if __name__ == "__main__":
    main()
