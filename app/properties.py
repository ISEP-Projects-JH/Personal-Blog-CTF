import os

def get_env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    if len(value) < 3:
        return default
    return value


def get_env_path(name: str, default: str) -> str:
    value = get_env_str(name, default)
    if not value.startswith("/"):
        value = "/" + value
    return value


def get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value, 0)  # support 0x / 0o / 0b
    except (ValueError, TypeError):
        return default

JWT_SECRET_USER = get_env_str(
    "JWT_SECRET_USER",
    "dev-secret-for-ctf-user"
)

JWT_SECRET_ADMIN = get_env_str(
    "JWT_SECRET_ADMIN",
    "dev-secret-for-ctf-admin"
)

JWT_ALGO = get_env_str(
    "JWT_ALGO",
    "HS256"
)

JWT_EXPIRE_SECONDS = get_env_int(
    "JWT_EXPIRE_SECONDS",
    3600
)

# User-side secret fragments
USER_MID_1 = get_env_str(
    "USER_MID_1",
    "user_mid_1_example"
)

USER_MID_2 = get_env_str(
    "USER_MID_2",
    "user_mid_2_cool"
)

# Admin-side secret fragments
ADMIN_MID_1 = get_env_str(
    "ADMIN_MID_1",
    "admin_mid_1_rootpower"
)

ADMIN_MID_2 = get_env_str(
    "ADMIN_MID_2",
    "admin_mid_2_adminonly"
)

ADD_NUM = get_env_int(
    "ADD_NUM",
    0xEEE7
)

ADMIN_URL = get_env_path(
    "ADMIN_URL",
    "/admin123"
)

ADMIN_LOGIN_URL = get_env_path(
    "ADMIN_LOGIN_URL",
    "/admin456_login"
)

CONFIG_JSON_PATH = get_env_str(
    "CONFIG_JSON_PATH",
    "config"
)
