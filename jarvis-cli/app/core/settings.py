"""
app/core/config.py — Decide qué cliente usar.
"""

import json
from pathlib import Path
from app.api.local_client import LocalJarvisClient
from app.api.http_client import HttpJarvisClient

CONFIG_PATH = Path.home() / ".jarvis" / "client_settings.json"


def get_client():
    modo = "dev"          
    backend_url = "http://localhost:5000"

    if CONFIG_PATH.exists():
        cfg = json.loads(CONFIG_PATH.read_text())
        modo = cfg.get("modo", modo)
        backend_url = cfg.get("backend_url", backend_url)

    if modo == "dev":
        return LocalJarvisClient()
    return HttpJarvisClient(base_url=backend_url)