import json
from pathlib import Path

SETTINGS_FILE = Path("application/user_settings.json")


def load_user_settings():
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open(encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_user_settings(data: dict):
    with SETTINGS_FILE.open(mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
