import json
import os

from .properties import (ADMIN_LOGIN_URL, ADMIN_URL, CONFIG_JSON_PATH)

CONFIG_JSON: dict = {
    "title": "Personal Blog Backend — CTF Service",

    "notice": {
        "scope": "single-player",
        "mode": "teaching",
    },

    "guidance": {
        "overview": [
            "This service behaves like a normal web application.",
            "Some responses may contain more information than expected.",
            "Not all useful data is protected by authentication.",
            "Observe carefully before attempting authentication.",
        ],
        "restrictions": [
            "Server-side filtering is active.",
            "Certain logical operators and keywords are blocked.",
            "Regex-based rules exist but are not disclosed.",
        ],
        "hint": [
            "You are not expected to guess identities.",
            "Valid targets appear naturally during normal interaction.",
        ],
    },

    "urls": {
        "you may want to visit": ["/api/home", "GET"],
        "user_answer": ["/api/user/answer/{jwt}", "POST"],

        "admin_login": [ADMIN_LOGIN_URL, "GET"],
        "admin_panel": [ADMIN_URL, "GET"],
        "admin_answer": ["/api/admin/answer/{jwt}", "POST"],

        "scoreboard": ["/api/flags", "GET"],
    },
}

def dump_config():
    """
    Dump CONFIG_JSON into static/{CONFIG_JSON_PATH}.json

    Assumes:
    - process is run from project root
    - ./static directory exists
    """
    static_dir = "static"
    os.makedirs(static_dir, exist_ok=True)

    output_path = os.path.join(static_dir, f"{CONFIG_JSON_PATH}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(CONFIG_JSON, f, indent=2, ensure_ascii=False) # noqa

    return output_path
