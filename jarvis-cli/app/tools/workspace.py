# app/tools/workspace.py (CLI)
import os 
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(r"C:\work\mcp-nexus\mcp-scratch\backend")
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


# --- Tools para el cli desde el langgrah backend agent ---
def set_agent_workspace(user_id: str, cwd: str | None = None) -> str:
    from src.services.agent.Koda.tools.delegation import set_workspace_direct
    return set_workspace_direct(user_id, cwd or os.getcwd())