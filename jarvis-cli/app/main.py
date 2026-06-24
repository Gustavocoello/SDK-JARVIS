"""
app/main.py — Punto de entrada del CLI.
"""
import logging
logging.disable(logging.WARNING)

import os
import signal
import sys
import asyncio
import typer
from dotenv import load_dotenv

# --- MAGIA DEL AUTOCOMPLETADO (TAB) ---
from prompt_toolkit.completion import WordCompleter

from app.ui.banner import welcome
from app.core.settings import get_client
from app.core.logging import setup_logging
from app.core.logging import silenciar_logs_para_cli
from app.core.auth import get_cached_user_id, save_user_id, resolve_user_id_by_email
from app.scripts.chat_loop import chat_loop

load_dotenv()
silenciar_logs_para_cli() 

def force_exit_handler(sig, frame):
    """Intercepta Ctrl+C a nivel de SO y mata el proceso al instante."""
    print("\nHasta la próxima ...")
    os._exit(0)

# Registramos el botón de pánico
signal.signal(signal.SIGINT, force_exit_handler)

app = typer.Typer()

@app.command()
def run (debug: bool = typer.Option(False, "--debug", help="Mostrar logs completos del backend")):
    """Arranca el chat interactivo de JARVIS."""
    if not debug:
        silenciar_logs_para_cli()
        setup_logging()
    asyncio.run(chat_loop())


if __name__ == "__main__":
    app()