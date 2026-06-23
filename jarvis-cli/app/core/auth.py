"""
app/core/auth.py — Resuelve y cachea el user_id real (UUID) localmente,
para no tener que loguearse cada vez que abrís el CLI.
"""

import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".jarvis" / "user.json"


def get_cached_user_id() -> str | None:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text()).get("user_id")
        except json.JSONDecodeError:
            return None
    return None


def save_user_id(user_id: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({"user_id": user_id}, indent=2))


def resolve_user_id_by_email(email: str) -> str | None:
    """
    Modo dev: consulta directo la tabla users (mismo approach que ya
    usa is_local_admin en delegation.py). En modo http, esto lo resolvería
    el backend vía Clerk en vez de esta función.
    """
    from src.database.settings.connection import get_db
    from src.database.models.models import User

    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == email).first()
        return str(user.id) if user else None
    finally:
        db.close()