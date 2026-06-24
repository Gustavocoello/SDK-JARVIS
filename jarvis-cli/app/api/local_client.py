"""
app/api/local_client.py — Modo "dev": import directo del backend, sin red.
Replica la MISMA lógica de parseo de [THOUGHT] que usa chat_v2_router,
para que CLI y frontend muestren el mismo nivel de detalle del agente.
"""

import sys
import json
import asyncio
from typing import AsyncIterator
from pathlib import Path

from langchain_core.messages import AIMessage, ToolMessage

from app.api.base import JarvisClientBase

BACKEND_ROOT = Path(r"C:\work\mcp-nexus\mcp-scratch\backend")
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.services.agent.jarvis.agent import get_jarvis 
from src.services.agent.nexus.agent import get_nexus
from src.services.agent.ragel.agent import get_ragel
from src.services.agent.Koda.agent import get_koda
from src.services.agent.lamar.agent import get_lamar


class LocalJarvisClient(JarvisClientBase):
    def __init__(self):
        self.active_agent = "jarvis"
        
        # Diccionario (Factory) con los inicializadores de cada agente
        self._agents = {
            "jarvis": get_jarvis,
            "nexus": get_nexus,
            "ragel": get_ragel,
            "koda": get_koda,
            "lamar": get_lamar
        }
    def set_agent(self, agent_name: str):
        """Permite al CLI cambiar el agente con el que se está comunicando."""
        if agent_name in self._agents:
            self.active_agent = agent_name
        else:
            raise ValueError(f"Agente desconocido: {agent_name}")

    async def enviar_mensaje_stream(self, mensaje: str, user_id: str, chat_id: str, thread_id: str) -> AsyncIterator[str]:
        factory = self._agents[self.active_agent]
        
        if self.active_agent in ["jarvis", "koda"]:
            agent = factory(user_id=user_id, client_type="cli")
        else:
            agent = factory(user_id=user_id)

        # stream_task() es SÍNCRONO (usa .stream() de LangGraph, no astream).
        # Lo corremos en un hilo aparte para no bloquear el event loop del CLI.
        loop = asyncio.get_event_loop()
        gen = agent.stream_task(mensaje, user_id, chat_id, thread_id)
        # Context Rules - Skills - MCP
        context = getattr(agent, '_last_context', {})
        if context:
            yield f"[CONTEXT]{json.dumps(context)}"

        def siguiente(g):
            try:
                return next(g)
            except StopIteration:
                return None

        while True:
            state_chunk = await loop.run_in_executor(None, siguiente, gen)
            if state_chunk is None:
                break

            messages = state_chunk.get("messages", [])
            if not messages:
                continue

            last_msg = messages[-1]

            # CASO A: el LLM decidió usar una herramienta
            if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
                for tool_call in last_msg.tool_calls:
                    t_name = tool_call.get("name", "UnknownTool")
                    t_args = tool_call.get("args", {})
                    args_str = json.dumps(t_args, ensure_ascii=False) if t_args else "{}"
                    yield f"[THOUGHT] Ejecutando herramienta '{t_name}'.\n"
                    yield f"[THOUGHT] Parámetros: {args_str}\n"

            # CASO B: la herramienta devolvió resultado
            elif isinstance(last_msg, ToolMessage):
                yield f"[THOUGHT] Herramienta '{last_msg.name}' completada. Evaluando resultado...\n"

            # CASO C: respuesta final del agente
            elif isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
                yield f"[THOUGHT] Generando respuesta final...\n"
                yield last_msg.content