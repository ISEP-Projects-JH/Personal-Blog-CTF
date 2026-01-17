import hashlib
import time

import jwt

from .properties import (
JWT_SECRET_USER, JWT_SECRET_ADMIN, JWT_ALGO, JWT_EXPIRE_SECONDS,
USER_MID_1, USER_MID_2, ADMIN_MID_1, ADMIN_MID_2, ADD_NUM
)

def make_user_proof(username: str, email: str, ts: int) -> str:
    """
    Generate a short proof string bound to user identity and login timestamp
    """
    base = f"{username}{USER_MID_1}{email}{USER_MID_2}{ts}"
    h = hashlib.sha256(base.encode()).hexdigest()
    num = int(h, 16) + ADD_NUM
    return hex(num)[2:].upper()[-4:]


def make_user_token(username: str, email: str) -> str:
    """
    Create a signed JWT for a normal user
    """
    ts = int(time.time())
    payload = {
        "role": "user",
        "username": username,
        "email": email,
        "login_ts": ts,
        "proof": make_user_proof(username, email, ts),
        "exp": ts + JWT_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET_USER, algorithm=JWT_ALGO)


def verify_user_token(token: str, username: str) -> dict | None:
    """
    Verify user JWT integrity and bind it to the requested username
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_USER,
            algorithms=[JWT_ALGO],
        )

        if payload.get("role") != "user":
            return None

        if payload["username"] != username:
            return None

        expect = make_user_proof(
            payload["username"],
            payload["email"],
            payload["login_ts"],
        )

        if payload["proof"] != expect:
            return None

        return payload

    except jwt.PyJWTError:
        return None


# =========================
# Admin JWT Helpers
# =========================

def make_admin_proof(username: str, ts: int) -> str:
    """
    Generate a short proof string for admin tokens
    """
    base = f"{username}{ADMIN_MID_1}{ADMIN_MID_2}{ts}"
    h = hashlib.sha256(base.encode()).hexdigest()
    num = int(h, 16) + ADD_NUM
    return hex(num)[2:].upper()[-4:]


def make_admin_token(username: str) -> str:
    """
    Create a signed JWT for admin users
    """
    ts = int(time.time())
    payload = {
        "role": "admin",
        "username": username,
        "login_ts": ts,
        "proof": make_admin_proof(username, ts),
        "exp": ts + JWT_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET_ADMIN, algorithm=JWT_ALGO)


def verify_admin_token(token: str) -> dict | None:
    """
    Verify admin JWT integrity
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_ADMIN,
            algorithms=[JWT_ALGO],
        )

        if payload.get("role") != "admin":
            return None

        expect = make_admin_proof(
            payload["username"],
            payload["login_ts"],
        )

        if payload["proof"] != expect:
            return None

        return payload

    except jwt.PyJWTError:
        return None

