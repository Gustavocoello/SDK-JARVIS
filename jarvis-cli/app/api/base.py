"""
app/api/base.py — Interfaz común. Ambos clientes (local e http) la implementan,
así el resto del CLI no le importa cuál está usando.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator


class JarvisClientBase(ABC):
    @abstractmethod
    async def enviar_mensaje_stream(
        self, mensaje: str, user_id: str, chat_id: str, thread_id: str
    ) -> AsyncIterator[str]:
        ...