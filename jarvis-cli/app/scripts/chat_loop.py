"""
app/scripts/chat_loop.py — Motor principal del chat interactivo.
"""
import os
import sys
import uuid
import json
import time
import asyncio
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
import pyperclip
import questionary
from app.ui.banner import welcome
from app.core.settings import get_client
from app.core.auth import get_cached_user_id, save_user_id

BACKEND_ROOT = Path(r"C:\work\mcp-nexus\mcp-scratch\backend")
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.services.agent.common.utils.history_fetcher import get_recent_sessions
from src.services.agent.jarvis.agent import _jarvis_cache
from src.services.agent.Koda.security.hitl import (
    get_pending_hitl_requests, 
    resolve_hitl_log, 
    resume_session,
    fail_session
)

console = Console()

def get_user_id() -> str:
    user_id = get_cached_user_id()
    if user_id:
        return user_id

    console.print("[yellow]Primera vez — pegá tu user_id (UUID)[/yellow]")
    user_id = Prompt.ask("user_id")
    save_user_id(user_id)
    return user_id

# ==========================================
# MENÚ DE HISTORIAL (Con tus colores exactos)
# ==========================================
menu_style = questionary.Style([
    ('pointer', 'fg:#FFFFFF bold'),      # El punto blanco
    ('highlighted', 'fg:#D2A541 bold'),  # Texto resaltado 
    ('selected', 'fg:#8E8E93'),     # Texto normal gris
    ('instruction', 'fg:#8E8E93'),       # Instrucciones atenuadas
])

async def handle_history_command(user_id: str) -> str | None:
    """
    Muestra el menú interactivo con flechas para seleccionar un chat antiguo.
    """
    recent_sessions = get_recent_sessions(user_id, limit=15)
    
    if not recent_sessions:
        console.print("[#8E8E93]No se encontraron conversaciones previas.[/#8E8E93]")
        return None

    choices = []
    for session in recent_sessions:
        title = f"{session['date']} | {session['summary']}"
        choices.append(questionary.Choice(title=title, value=session['session_id']))

    choices.append(questionary.Choice(title="Cancelar", value=None))

    try:
        selected_session_id = await questionary.select(
            "Selecciona una conversación para reanudar:",
            choices=choices,
            style=menu_style,
            qmark="",             # Quita el '?'
            pointer="●",          # Cambia la flecha por el punto
            instruction=" (Usa ⬆/⬇, Enter para seleccionar)"
        ).ask_async()
        
        return selected_session_id
    except KeyboardInterrupt:
        return None
    
# ==========================================
#  AGENTES CAMBIO DINAMICO
# ==========================================
async def handle_agentes_command() -> str | None:
    """
    Muestra el menú interactivo para seleccionar con qué agente hablar directamente.
    """
    choices = [
        questionary.Choice(title="Jarvis (Orquestador General)", value="jarvis"),
        questionary.Choice(title="Koda (Ingeniero de Software)", value="koda"),
        questionary.Choice(title="Nexus (Productividad - MCP Orquestador)", value="nexus"),
        questionary.Choice(title="Ragel (Investigador / Documentos / Web)", value="ragel"),
        questionary.Choice(title="Lamar (DevOps / Admin / Servidores)", value="lamar"),
        questionary.Choice(title="Cancelar", value=None)
    ]

    try:
        selected_agent = await questionary.select(
            "Selecciona el agente con el que deseas interactuar:",
            choices=choices,
            style=menu_style,
            qmark="",            
            pointer="●",          
            instruction=" (Usa ⬆/⬇, Enter para seleccionar)"
        ).ask_async()
        
        return selected_agent
    except KeyboardInterrupt:
        return None

async def chat_loop():
    await welcome()
    user_id = get_user_id()
    client  = get_client()
    chat_id = str(uuid.uuid4())
    thread_id = str(uuid.uuid4())
    current_session_id = None
    last_ai_response = ""
    active_agent_name = "jarvis" # Agente por defecto
    console.print("\nJARVIS CLI READY! Escribe [bold #D2A541]/help[/bold #D2A541] para ver comandos.\n")

    while True:
        # ==========================================
        # 1. INTERCEPTOR DE SEGURIDAD (HITL)
        # Revisa si hay bloqueos ANTES de pedir tu input
        # ==========================================
        try:
            pending_requests = get_pending_hitl_requests(user_id)
            if pending_requests:
                console.print("\n[bold red]ACCIONES PENDIENTES DE APROBACIÓN (HITL)[/bold red]")
                
                for req in pending_requests:
                    console.print(f"  [yellow]Herramienta:[/yellow] {req['tool']}")
                    console.print(f"  [yellow]Regla Rota:[/yellow]  {req['matched']}")
                    console.print(f"  [yellow]Comando:[/yellow]     {req['input'][:200]}...\n")
                    
                    # Menú interactivo de decisión
                    choice = await questionary.select(
                        "¿Qué deseas hacer con esta acción bloqueada?",
                        choices=["Aprobar y Continuar", "Rechazar y Cancelar", "Ignorar por ahora"],
                        style=menu_style,
                        qmark="🛡️",
                        pointer="●"
                    ).ask_async()

                    if choice == "Aprobar y Continuar":
                        resolve_hitl_log(req['id'], user_id, approved=True, note="Aprobado vía CLI")
                        if req.get('session_id'): resume_session(req['session_id'])
                        console.print("[bold green]✔ Acción aprobada. Jarvis prosigue...[/bold green]\n")
                        
                    elif choice == "Rechazar y Cancelar":
                        resolve_hitl_log(req['id'], user_id, approved=False, note="Rechazado vía CLI")
                        if req.get('session_id'): fail_session(req['session_id'], "HITL Rechazado por el usuario.")
                        console.print("[bold red]Acción rechazada y cancelada.[/bold red]\n")
                        
                # Si resolvió un HITL, reiniciamos el ciclo por si hay más
                continue
        except Exception:
            pass # Si falla la conexión a DB, ignoramos para no romper el chat
        # Estilo terminal: "gustavocoello$ " en vez de "╭─ Tú / ╰─>"
        usuario_input = Prompt.ask(f"[bold green]{user_id[:8]}[/bold green][bold white]$[/bold white]")

        if not usuario_input:
            continue
            
        command = usuario_input.strip().lower()

        # ==========================================
        # COMANDOS CLI
        # ==========================================
        if command in ["/salir", "salir", "/exit", "exit", "/quit", "quit", "/q", "q"]:
            console.print("\n[bold #D2A541]Desconectando... ¡Adiós![/bold #D2A541] 👋\n")
            break
            
        elif command == "/help":
            help_text = """
            **Comandos CLI:**
            - `/history` : Selecciona una conversación anterior con flechas ⬆/⬇.
            - `/agentes` : Cambia el agente activo (Jarvis, Koda, Nexus, Ragel, Lamar).
            - `/new`     : Inicia una nueva sesión limpia.
            - `/copy`    : Copia la última respuesta al portapapeles.
            - `/clear`   : Limpia la pantalla de la terminal.
            - `/reboot`  : Recarga a Jarvis y lee de nuevo el AGENT.md.
            - `/help`    : Muestra esta lista de comandos.
            - `/exit`    : Desconecta y cierra JARVIS.
            """
            console.print(Markdown(help_text))
            continue
        elif command == "/clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        elif command == "/new":
            chat_id = str(uuid.uuid4())
            last_ai_response = "" # Limpiamos también el copy
            console.print("[#8E8E93]Iniciada una nueva sesión conversacional.[/#8E8E93]")
            continue
        elif command == "/copy":
            if last_ai_response:
                pyperclip.copy(last_ai_response)
                console.print("[#D1D1D6]¡Última respuesta copiada al portapapeles![/#D1D1D6]")
            else:
                console.print("[#8E8E93]Nada que copiar aún.[/#8E8E93]")
            continue
        elif command == "/history":
                selected_id = await handle_history_command(user_id)
                if selected_id:
                    # ¡CLAVE! Actualizamos AMBOS IDs para reanudar la memoria correctamente
                    chat_id = selected_id
                    current_session_id = selected_id
                    console.print(f"[#D2A541]Sesión reanudada:[/#D2A541] [#D1D1D6]{chat_id}[/#D1D1D6]")
                continue
        elif command in ["/reboot", "/reload", "/restart"]:
            chat_id = str(uuid.uuid4())
            current_session_id = None
            last_ai_response = ""
            try:
                _jarvis_cache.clear()
            except ImportError:
                pass # Si estás en modo HTTP remoto, ignoramos esto
            client = get_client()
            console.print("[bold #D2A541]Jarvis reloaded with updated AGENT.md and cleared cache.[/bold #D2A541]")
            continue
        elif command in ["/agentes", "/agents"]:
            nuevo_agente = await handle_agentes_command()
            if nuevo_agente:
                # Actualizamos la variable local de UI
                active_agent_name = nuevo_agente
                # Le decimos al cliente que cambie de cerebro
                if hasattr(client, 'set_agent'):
                    client.set_agent(nuevo_agente)
                
                console.print(f"\n[bold #D2A541]¡Enlace establecido![/bold #D2A541] Ahora interactúas directamente con [bold white]{nuevo_agente.upper()}[/bold white].")
            continue
        
        # ==========================================
        # FUNCIONES DE UI LOCALES
        # ==========================================
        def _render_context_bar(ctx_data: dict):
            """Muestra la barra de contexto activo en dim, solo los que aplican."""
            parts = []
            rules = ctx_data.get("rules", [])
            mcp = ctx_data.get("mcp", 0)
            skills = ctx_data.get("skills", 0)

            if rules:
                # Mapeo legible de nombres internos
                labels = {
                    "anti_hallucination": "Anti-Hallucination",
                    "skills_workflow": "Skills",
                    "file_operations": "Files",
                }
                rule_labels = [labels.get(r, r) for r in rules]
                parts.append(f"Rules: {', '.join(rule_labels)}")
            
            # Mostramos Skills y MCP si el backend nos indicó que se invocaron
            if skills > 0: parts.append(f"Skills: {skills}")
            if mcp > 0: parts.append(f"MCP: {mcp}")

            if parts:
                console.print(f"  [dim]· {' · '.join(parts)}[/dim]")

        # ==========================================
        # FLUJO NORMAL DE CHAT
        # ==========================================
        console.print(f"\n[bold cyan]{active_agent_name}-agent[/bold cyan]")
        respuesta_final = ""
        cwd = os.getcwd()
        instruction_with_context = f"[SYSTEM: User is currently at directory: {cwd}]\n\n{usuario_input}"
        
        # Badges para Skills; Rules ; MCP 
        context_rendered = False          
        start_time = time.time()

        try:
            with console.status("[#8E8E93]Procesando... 0.0s[/#8E8E93]", spinner="dots", spinner_style="bold #D2A541") as status:
                
                # 1. CREAMOS UNA TAREA EN SEGUNDO PLANO PARA EL RELOJ
                async def update_timer():
                    try:
                        while True:
                            elapsed = time.time() - start_time
                            status.update(f"[#8E8E93]Procesando... {elapsed:.1f}s[/#8E8E93]")
                            await asyncio.sleep(0.1) # Se actualiza 10 veces por segundo
                    except asyncio.CancelledError:
                        pass # Termina silenciosamente cuando la cancelamos
                
                # Arrancamos el reloj en paralelo
                timer_task = asyncio.create_task(update_timer())
                
                try:
                    # 2. ESCUCHAMOS EL SERVIDOR MIENTRAS EL RELOJ GIRA
                    async for chunk in client.enviar_mensaje_stream(instruction_with_context, user_id, chat_id, thread_id):
                        if chunk.startswith("[CONTEXT]"):
                            if not context_rendered:
                                try:
                                    context_str = chunk.replace("[CONTEXT]", "").strip()
                                    context_data = json.loads(context_str)
                                    _render_context_bar(context_data)
                                    context_rendered = True
                                except Exception:
                                    pass
                            continue
                        elif chunk.startswith("[THOUGHT]"):
                            texto_pensamiento = chunk.replace("[THOUGHT]", "").strip()
                            texto_lower = texto_pensamiento.lower()
                            console.print(f"  [dim italic]· {texto_pensamiento}[/dim italic]")
                        else:
                            respuesta_final += chunk
                finally:
                    # 3. APAGAMOS EL RELOJ AL TERMINAR (pase lo que pase)
                    timer_task.cancel()

            # 4. IMPRIMIMOS EL MARKDOWN
            if respuesta_final:
                console.print(Markdown(respuesta_final))
                last_ai_response = respuesta_final
                
            # 5. TIEMPO FINAL A LA DERECHA
            total_elapsed = time.time() - start_time
            console.print(f"[#8E8E93]{total_elapsed:.2f}s[/#8E8E93]", justify="right")
        
        except KeyboardInterrupt:
            # En lugar de continuar, forzamos un cierre instantáneo a nivel del Sistema Operativo
            console.print("\n[bold #D2A541]Cierre forzado detectado (Ctrl+C). Apagando JARVIS al instante...[/bold #D2A541] 🛑")
            os._exit(0)          
        
        except Exception as e:
            console.print(f"[bold red]Error en backend:[/bold red] {str(e)}")
            
        console.print()